from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import json
import time
import os
import tempfile
import shutil
from datetime import datetime
import logging
from core.langgraph_mcp import LangGraphMCP
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP-Driven Multi-Modal AI Assistant", 
    version="2.0.0",
    description="Advanced AI assistant with LangGraph orchestration and multi-modal capabilities"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

for directory in [STATIC_DIR, AUDIO_DIR, UPLOAD_DIR]:
    os.makedirs(directory, exist_ok=True)

# Initialize configuration and MCP
config = Config()
mcp = LangGraphMCP(config)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    enable_tts: Optional[bool] = False
    session_id: Optional[str] = None

class MultiModalQueryRequest(BaseModel):
    query: str
    enable_tts: Optional[bool] = False
    session_id: Optional[str] = None
    file_type: Optional[str] = None

class QueryResponse(BaseModel):
    session_id: str
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    steps: Optional[List] = None
    timestamp: str

class DocumentUploadRequest(BaseModel):
    file_path: str
    chunk_size: Optional[int] = 1000
    overlap: Optional[int] = 200

@app.get("/")
async def root():
    return {
        "message": "MCP-Driven Multi-Modal AI Assistant API",
        "version": "2.0.0",
        "features": [
            "LangGraph orchestration",
            "Multi-modal input support",
            "Vector store integration",
            "Memory management",
            "Quality control with critique agent"
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Check Ollama connection
        ollama_status = "unknown"
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{config.ollama_host}/api/tags") as response:
                    if response.status == 200:
                        ollama_status = "connected"
                    else:
                        ollama_status = "error"
        except:
            ollama_status = "disconnected"
        
        # Get system stats
        vector_stats = mcp.get_vector_store_stats()
        memory_stats = mcp.get_memory_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "ollama_status": ollama_status,
            "vector_store": vector_stats,
            "memory": memory_stats,
            "config": {
                "tts_enabled": config.tts_enabled,
                "stt_enabled": config.stt_enabled,
                "models": {
                    "llm": config.ollama_model,
                    "vision": config.ollama_vision_model,
                    "whisper": config.whisper_model
                }
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Process text query"""
    try:
        logger.info(f"Received text query: {request.query}")
        
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{int(time.time())}"
        
        # Process query through LangGraph MCP
        result = await mcp.process_query(
            query=request.query,
            session_id=session_id,
            enable_tts=bool(request.enable_tts)
        )
        
        return QueryResponse(
            session_id=session_id,
            status="success",
            message="Query processed successfully",
            data=result,
            steps=result.get("steps", []),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing text query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    query: str = Form(...),
    enable_tts: bool = Form(False),
    session_id: Optional[str] = Form(None)
):
    """Upload and process file with query"""
    try:
        logger.info(f"Received file upload: {file.filename}")
        
        # Validate file size
        if file.size and file.size > config.max_file_size:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Generate session ID if not provided
        session_id = session_id or f"session_{int(time.time())}"
        
        # Save uploaded file
        file_extension = os.path.splitext(file.filename)[1].lower()
        temp_filename = f"{session_id}_{int(time.time())}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, temp_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process through LangGraph MCP
        result = await mcp.process_query(
            query=query,
            session_id=session_id,
            enable_tts=enable_tts,
            file_path=file_path
        )
        
        # Clean up uploaded file after processing
        try:
            os.remove(file_path)
        except:
            pass
        
        return QueryResponse(
            session_id=session_id,
            status="success",
            message="File processed successfully",
            data=result,
            steps=result.get("steps", []),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/add")
async def add_document_to_vectorstore(request: DocumentUploadRequest):
    """Add document to vector store for future retrieval"""
    try:
        file_path = request.file_path
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Process document based on type
        from agents.multimodal_agents import DocumentProcessor
        
        if file_path.lower().endswith('.pdf'):
            content = DocumentProcessor.process_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            content = DocumentProcessor.process_docx(file_path)
        elif file_path.lower().endswith('.txt'):
            content = DocumentProcessor.process_txt(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Chunk and add to vector store
        chunks = DocumentProcessor.chunk_text(
            content, 
            chunk_size=request.chunk_size,
            overlap=request.overlap
        )
        
        doc_ids = mcp.vector_store.add_documents(chunks, [
            {
                "source": file_path,
                "chunk_id": i,
                "filename": os.path.basename(file_path),
                "added_at": datetime.now().isoformat()
            }
            for i in range(len(chunks))
        ])
        
        return {
            "message": f"Added {len(chunks)} chunks to vector store",
            "document_ids": doc_ids,
            "chunks_count": len(chunks),
            "source": file_path
        }
        
    except Exception as e:
        logger.error(f"Error adding document to vector store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/search")
async def search_documents(query: str, limit: int = 5):
    """Search documents in vector store"""
    try:
        results = mcp.vector_store.search(query, n_results=limit)
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{session_id}")
async def get_status(session_id: str):
    """Get session status"""
    try:
        status = await mcp.get_session_status(session_id)
        return status
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 10):
    """Get conversation history for session"""
    try:
        history = mcp.memory_manager.get_conversation_history(session_id, limit)
        return {
            "session_id": session_id,
            "history": history,
            "total_messages": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting session history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/context")
async def set_session_context(session_id: str, context: Dict[str, Any]):
    """Set context for session"""
    try:
        for key, value in context.items():
            mcp.memory_manager.set_context(session_id, key, value)
        
        return {
            "message": "Context updated successfully",
            "session_id": session_id,
            "context_keys": list(context.keys())
        }
    except Exception as e:
        logger.error(f"Error setting session context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def get_agents():
    """Get information about available agents"""
    return {
        "agents": [
            {
                "name": "Intent Agent",
                "type": "classification",
                "description": "Classifies user intent and extracts entities",
                "capabilities": ["intent_classification", "entity_extraction"]
            },
            {
                "name": "Research Agent",
                "type": "research",
                "description": "Conducts comprehensive research using local LLM",
                "capabilities": ["research", "analysis", "fact_finding"]
            },
            {
                "name": "Compare Agent",
                "type": "comparison",
                "description": "Compares entities and concepts",
                "capabilities": ["comparison", "analysis", "evaluation"]
            },
            {
                "name": "Summarizer Agent",
                "type": "summarization",
                "description": "Summarizes content and extracts key points",
                "capabilities": ["summarization", "key_point_extraction"]
            },
            {
                "name": "Retriever Agent",
                "type": "retrieval",
                "description": "Searches vector store for relevant information",
                "capabilities": ["document_search", "context_retrieval"]
            },
            {
                "name": "Vision Agent",
                "type": "vision",
                "description": "Analyzes images using LLaVA model",
                "capabilities": ["image_analysis", "visual_understanding"]
            },
            {
                "name": "OCR Agent",
                "type": "ocr",
                "description": "Extracts text from images",
                "capabilities": ["text_extraction", "document_digitization"]
            },
            {
                "name": "STT Agent",
                "type": "speech",
                "description": "Converts speech to text using Whisper",
                "capabilities": ["speech_recognition", "audio_transcription"]
            },
            {
                "name": "TTS Agent",
                "type": "speech",
                "description": "Converts text to speech",
                "capabilities": ["text_to_speech", "audio_generation"]
            },
            {
                "name": "Critique Agent",
                "type": "quality_control",
                "description": "Evaluates response quality and suggests improvements",
                "capabilities": ["quality_assessment", "response_evaluation"]
            }
        ],
        "workflow": "LangGraph-based orchestration with conditional routing"
    }

@app.get("/stats")
async def get_system_stats():
    """Get comprehensive system statistics"""
    try:
        vector_stats = mcp.get_vector_store_stats()
        memory_stats = mcp.get_memory_stats()
        
        return {
            "vector_store": vector_stats,
            "memory": memory_stats,
            "active_sessions": len(mcp.sessions),
            "upload_directory": UPLOAD_DIR,
            "audio_directory": AUDIO_DIR
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup")
async def cleanup_system():
    """Clean up old sessions and temporary files"""
    try:
        # Clean up old sessions
        mcp.memory_manager.cleanup_old_sessions(days=7)
        
        # Clean up old uploaded files
        cleanup_count = 0
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                # Remove files older than 1 day
                if time.time() - os.path.getctime(file_path) > 86400:
                    os.remove(file_path)
                    cleanup_count += 1
        
        return {
            "message": "Cleanup completed successfully",
            "files_removed": cleanup_count
        }
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static directories
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)