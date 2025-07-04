from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Request
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

# Import all the new modules
from core.langgraph_mcp import LangGraphMCP
from core.streaming import streaming_service
from auth.supabase_auth import auth_service, get_current_user, get_optional_user
from multilingual.language_service import multilingual_service
from debug.developer_mode import developer_mode
from plugins.plugin_loader import plugin_loader
from enhanced_memory.redis_memory import enhanced_memory
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Neurofluxion AI - Production Ready", 
    version="3.0.0",
    description="Complete production-ready AI assistant with streaming, auth, multilingual support, and developer tools"
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

# Load plugins on startup
plugin_loader.load_all_plugins()

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    enable_tts: Optional[bool] = False
    session_id: Optional[str] = None
    language: Optional[str] = 'en'
    enable_streaming: Optional[bool] = False

class AuthRequest(BaseModel):
    email: str
    password: str
    metadata: Optional[Dict[str, Any]] = None

class PreferencesRequest(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    tts_enabled: Optional[bool] = None
    voice_speed: Optional[int] = None

class DebugRequest(BaseModel):
    session_id: str
    enable: bool

@app.get("/")
async def root():
    return {
        "message": "Neurofluxion AI - Production Ready",
        "version": "3.0.0",
        "features": [
            "Real-time streaming output",
            "User authentication & sessions",
            "Multilingual support (12 languages)",
            "Developer debug mode",
            "Plugin system",
            "Enhanced memory with Redis",
            "Voice input/output",
            "Multi-modal processing"
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
        memory_stats = enhanced_memory.get_memory_stats()
        plugin_stats = plugin_loader.list_plugins()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "ollama_status": ollama_status,
            "vector_store": vector_stats,
            "memory": memory_stats,
            "plugins": {
                "loaded": len(plugin_stats),
                "available": plugin_stats
            },
            "multilingual": {
                "supported_languages": len(multilingual_service.get_supported_languages()),
                "languages": list(multilingual_service.get_supported_languages().keys())
            },
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

# Authentication endpoints
@app.post("/auth/register")
async def register(request: AuthRequest):
    """Register new user"""
    return await auth_service.register_user(request.email, request.password, request.metadata)

@app.post("/auth/login")
async def login(request: AuthRequest):
    """Login user"""
    return await auth_service.login_user(request.email, request.password)

@app.get("/auth/me")
async def get_me(current_user = Depends(get_current_user)):
    """Get current user info"""
    return {"user": current_user}

@app.put("/auth/preferences")
async def update_preferences(request: PreferencesRequest, current_user = Depends(get_current_user)):
    """Update user preferences"""
    preferences = request.dict(exclude_unset=True)
    updated_prefs = await auth_service.update_user_preferences(current_user["email"], preferences)
    return {"preferences": updated_prefs}

# Streaming endpoints
@app.get("/stream/{session_id}")
async def stream_session(session_id: str, request: Request):
    """Stream session progress and results"""
    async def generate_stream():
        async for update in streaming_service.stream_agent_progress(session_id, mcp):
            yield update
    
    return await streaming_service.create_sse_response(session_id, generate_stream())

@app.post("/ask")
async def ask_question(request: QueryRequest, current_user = Depends(get_optional_user)):
    """Process text query with optional streaming"""
    try:
        logger.info(f"Received query: {request.query}")
        
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{int(time.time())}"
        
        # Enable debug mode if user is authenticated
        if current_user:
            developer_mode.enable_debug(session_id)
            # Store user context
            enhanced_memory.set_user_memory(current_user["id"], "last_query", request.query)
        
        # Detect and translate if needed
        detected_lang = multilingual_service.detect_language(request.query)
        query_to_process = request.query
        
        if request.language != 'en' and detected_lang != request.language:
            query_to_process = multilingual_service.translate_text(
                request.query, 'en', detected_lang
            )
        
        # Process query through LangGraph MCP
        if request.enable_streaming:
            # Return streaming response
            async def generate_stream():
                async for update in streaming_service.stream_llm_response(session_id, query_to_process, mcp.llm):
                    yield update
            
            return await streaming_service.create_sse_response(session_id, generate_stream())
        else:
            # Regular processing
            result = await mcp.process_query(
                query=query_to_process,
                session_id=session_id,
                enable_tts=bool(request.enable_tts)
            )
            
            # Translate result if needed
            if request.language != 'en':
                result["summary"] = multilingual_service.translate_text(
                    result["summary"], request.language, 'en'
                )
            
            # Store conversation if user is authenticated
            if current_user:
                enhanced_memory.add_conversation_history(
                    current_user["id"], session_id, {
                        "type": "query",
                        "query": request.query,
                        "result": result
                    }
                )
            
            return {
                "session_id": session_id,
                "status": "success",
                "message": "Query processed successfully",
                "data": result,
                "language": request.language,
                "detected_language": detected_lang,
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        if current_user:
            developer_mode.log_error(session_id, "query_processing", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    query: str = Form(...),
    enable_tts: bool = Form(False),
    language: str = Form('en'),
    session_id: Optional[str] = Form(None),
    current_user = Depends(get_optional_user)
):
    """Upload and process file with query"""
    try:
        logger.info(f"Received file upload: {file.filename}")
        
        # Validate file size
        if file.size and file.size > config.max_file_size:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Generate session ID if not provided
        session_id = session_id or f"session_{int(time.time())}"
        
        if current_user:
            developer_mode.enable_debug(session_id)
        
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
        
        # Translate result if needed
        if language != 'en':
            result["summary"] = multilingual_service.translate_text(
                result["summary"], language, 'en'
            )
        
        # Store conversation if user is authenticated
        if current_user:
            enhanced_memory.add_conversation_history(
                current_user["id"], session_id, {
                    "type": "file_upload",
                    "filename": file.filename,
                    "query": query,
                    "result": result
                }
            )
        
        # Clean up uploaded file after processing
        try:
            os.remove(file_path)
        except:
            pass
        
        return {
            "session_id": session_id,
            "status": "success",
            "message": "File processed successfully",
            "data": result,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Developer mode endpoints
@app.post("/debug/toggle")
async def toggle_debug(request: DebugRequest, current_user = Depends(get_current_user)):
    """Toggle debug mode for session"""
    if request.enable:
        developer_mode.enable_debug(request.session_id)
    else:
        developer_mode.disable_debug(request.session_id)
    
    return {
        "session_id": request.session_id,
        "debug_enabled": request.enable,
        "message": f"Debug mode {'enabled' if request.enable else 'disabled'}"
    }

@app.get("/debug/logs/{session_id}")
async def get_debug_logs(session_id: str, log_type: Optional[str] = None, current_user = Depends(get_current_user)):
    """Get debug logs for session"""
    if log_type:
        logs = developer_mode.get_filtered_logs(session_id, log_type=log_type)
    else:
        logs = developer_mode.get_session_logs(session_id)
    
    return {
        "session_id": session_id,
        "logs": logs,
        "total_logs": len(logs)
    }

@app.get("/debug/performance/{session_id}")
async def get_performance_metrics(session_id: str, current_user = Depends(get_current_user)):
    """Get performance metrics for session"""
    metrics = developer_mode.get_performance_metrics(session_id)
    return {
        "session_id": session_id,
        "metrics": metrics
    }

# Plugin system endpoints
@app.get("/plugins")
async def list_plugins():
    """List all available plugins"""
    return {
        "plugins": plugin_loader.list_plugins(),
        "total_loaded": len(plugin_loader.loaded_plugins)
    }

@app.post("/plugins/reload")
async def reload_plugins(current_user = Depends(get_current_user)):
    """Reload all plugins"""
    result = plugin_loader.load_all_plugins()
    return {
        "message": "Plugins reloaded",
        "result": result
    }

# Multilingual endpoints
@app.get("/languages")
async def get_supported_languages():
    """Get supported languages"""
    return {
        "languages": multilingual_service.get_supported_languages(),
        "total_supported": len(multilingual_service.get_supported_languages())
    }

@app.post("/translate")
async def translate_text(text: str, target_language: str, source_language: Optional[str] = None):
    """Translate text"""
    if not source_language:
        source_language = multilingual_service.detect_language(text)
    
    translated = multilingual_service.translate_text(text, target_language, source_language)
    
    return {
        "original_text": text,
        "translated_text": translated,
        "source_language": source_language,
        "target_language": target_language
    }

# Memory and conversation endpoints
@app.get("/conversations")
async def get_conversations(current_user = Depends(get_current_user)):
    """Get user's conversation sessions"""
    sessions = enhanced_memory.get_user_sessions(current_user["id"])
    return {
        "sessions": sessions,
        "total_sessions": len(sessions)
    }

@app.get("/conversations/{session_id}/history")
async def get_conversation_history(session_id: str, limit: int = 10, current_user = Depends(get_current_user)):
    """Get conversation history for session"""
    history = enhanced_memory.get_conversation_history(current_user["id"], session_id, limit)
    return {
        "session_id": session_id,
        "history": history,
        "total_messages": len(history)
    }

# Existing endpoints (updated)
@app.get("/status/{session_id}")
async def get_status(session_id: str):
    """Get session status"""
    try:
        status = await mcp.get_session_status(session_id)
        return status
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/add")
async def add_document_to_vectorstore(file_path: str, chunk_size: int = 1000, overlap: int = 200):
    """Add document to vector store for future retrieval"""
    try:
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
        chunks = DocumentProcessor.chunk_text(content, chunk_size=chunk_size, overlap=overlap)
        
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

@app.get("/agents")
async def get_agents():
    """Get information about available agents"""
    base_agents = [
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
    ]
    
    # Add plugin agents
    plugin_agents = [
        {
            "name": plugin["name"],
            "type": "plugin",
            "description": plugin["description"],
            "capabilities": ["custom_processing"],
            "version": plugin["version"],
            "plugin": True
        }
        for plugin in plugin_loader.list_plugins()
    ]
    
    return {
        "base_agents": base_agents,
        "plugin_agents": plugin_agents,
        "total_agents": len(base_agents) + len(plugin_agents),
        "workflow": "LangGraph-based orchestration with conditional routing"
    }

@app.get("/stats")
async def get_system_stats():
    """Get comprehensive system statistics"""
    try:
        vector_stats = mcp.get_vector_store_stats()
        memory_stats = enhanced_memory.get_memory_stats()
        plugin_stats = plugin_loader.list_plugins()
        
        return {
            "vector_store": vector_stats,
            "memory": memory_stats,
            "plugins": {
                "loaded": len(plugin_stats),
                "available": plugin_stats
            },
            "active_sessions": len(mcp.sessions),
            "multilingual": {
                "supported_languages": len(multilingual_service.get_supported_languages())
            },
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
        enhanced_memory.cleanup_expired_data()
        
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