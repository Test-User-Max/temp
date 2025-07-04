from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from typing import Dict, Any, List, Optional, TypedDict
import asyncio
import time
import logging
from ..agents.langchain_agents import (
    IntentAgent, ResearchAgent, CompareAgent, SummarizerAgent, 
    RetrieverAgent, CritiqueAgent
)
from ..agents.multimodal_agents import VisionAgent, OCRAgent, STTAgent, TTSAgent
from ..core.llm_interface import OllamaLLM
from ..core.vectorstore import VectorStore
from ..core.memory import MemoryManager

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State for the agent workflow"""
    # Input
    query: str
    session_id: str
    input_type: str  # text, image, audio, document
    file_path: Optional[str]
    enable_tts: bool
    
    # Processing state
    intent: str
    confidence: float
    entities: List[str]
    context: Dict[str, Any]
    
    # Agent outputs
    research_content: str
    comparison_result: str
    vision_result: str
    ocr_result: str
    transcription: str
    retrieved_content: str
    summary: str
    key_points: List[str]
    
    # Quality control
    quality_score: float
    needs_improvement: bool
    retry_count: int
    
    # Final output
    final_result: Dict[str, Any]
    audio_file: Optional[str]
    
    # Metadata
    processing_steps: List[Dict[str, Any]]
    start_time: float
    current_step: int

class LangGraphMCP:
    """Multi-Agent Control Plane using LangGraph"""
    
    def __init__(self, config):
        self.config = config
        self.llm = OllamaLLM(host=config.ollama_host, model=config.ollama_model)
        self.vector_store = VectorStore(config.chroma_persist_directory)
        self.memory_manager = MemoryManager(config.memory_type)
        
        # Initialize agents
        self.intent_agent = IntentAgent("Intent Agent", self.llm, config)
        self.research_agent = ResearchAgent("Research Agent", self.llm, config)
        self.compare_agent = CompareAgent("Compare Agent", self.llm, config)
        self.summarizer_agent = SummarizerAgent("Summarizer Agent", self.llm, config)
        self.retriever_agent = RetrieverAgent("Retriever Agent", self.llm, config, self.vector_store)
        self.critique_agent = CritiqueAgent("Critique Agent", self.llm, config)
        
        # Multimodal agents
        self.vision_agent = VisionAgent("Vision Agent", self.llm, config)
        self.ocr_agent = OCRAgent("OCR Agent", self.llm, config)
        self.stt_agent = STTAgent("STT Agent", self.llm, config)
        self.tts_agent = TTSAgent("TTS Agent", self.llm, config)
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        self.sessions = {}
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("preprocess", self._preprocess_input)
        workflow.add_node("intent_classification", self._classify_intent)
        workflow.add_node("multimodal_processing", self._process_multimodal)
        workflow.add_node("research", self._research)
        workflow.add_node("compare", self._compare)
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("summarize", self._summarize)
        workflow.add_node("critique", self._critique)
        workflow.add_node("tts", self._text_to_speech)
        workflow.add_node("finalize", self._finalize_result)
        
        # Set entry point
        workflow.set_entry_point("preprocess")
        
        # Add edges
        workflow.add_edge("preprocess", "intent_classification")
        workflow.add_conditional_edges(
            "intent_classification",
            self._route_after_intent,
            {
                "multimodal": "multimodal_processing",
                "research": "research",
                "compare": "compare",
                "retrieve": "retrieve",
                "summarize": "summarize"
            }
        )
        
        # Multimodal processing routes
        workflow.add_edge("multimodal_processing", "summarize")
        
        # Research and comparison routes
        workflow.add_edge("research", "summarize")
        workflow.add_edge("compare", "summarize")
        workflow.add_edge("retrieve", "summarize")
        
        # Quality control
        workflow.add_conditional_edges(
            "summarize",
            self._should_critique,
            {
                "critique": "critique",
                "tts": "tts",
                "finalize": "finalize"
            }
        )
        
        workflow.add_conditional_edges(
            "critique",
            self._handle_critique_result,
            {
                "retry": "research",
                "tts": "tts",
                "finalize": "finalize"
            }
        )
        
        # Final processing
        workflow.add_conditional_edges(
            "tts",
            self._should_finalize,
            {
                "finalize": "finalize"
            }
        )
        
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def _preprocess_input(self, state: AgentState) -> AgentState:
        """Preprocess input and determine type"""
        await self._update_step(state, "Preprocessing input...", 1)
        
        # Determine input type
        if state.get("file_path"):
            file_path = state["file_path"]
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                state["input_type"] = "image"
            elif file_path.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
                state["input_type"] = "audio"
            elif file_path.lower().endswith(('.pdf', '.docx', '.txt')):
                state["input_type"] = "document"
            else:
                state["input_type"] = "unknown"
        else:
            state["input_type"] = "text"
        
        # Initialize processing metadata
        state["start_time"] = time.time()
        state["processing_steps"] = []
        state["current_step"] = 1
        state["retry_count"] = 0
        
        return state
    
    async def _classify_intent(self, state: AgentState) -> AgentState:
        """Classify user intent"""
        await self._update_step(state, "Understanding your query...", 2)
        
        try:
            result = await self.intent_agent.execute({
                "query": state["query"]
            })
            
            state["intent"] = result["intent"]
            state["confidence"] = result["confidence"]
            state["entities"] = result["entities"]
            
        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            state["intent"] = "general"
            state["confidence"] = 0.5
            state["entities"] = []
        
        return state
    
    async def _process_multimodal(self, state: AgentState) -> AgentState:
        """Process multimodal inputs"""
        input_type = state["input_type"]
        file_path = state.get("file_path", "")
        
        if input_type == "image":
            await self._update_step(state, "Analyzing image...", 3)
            
            # Try vision analysis first
            try:
                vision_result = await self.vision_agent.execute({
                    "image_path": file_path,
                    "prompt": f"Analyze this image in the context of: {state['query']}"
                })
                state["vision_result"] = vision_result["vision_result"]
            except Exception as e:
                logger.error(f"Vision analysis failed: {str(e)}")
                state["vision_result"] = ""
            
            # Try OCR as fallback or supplement
            try:
                ocr_result = await self.ocr_agent.execute({
                    "image_path": file_path
                })
                state["ocr_result"] = ocr_result["ocr_result"]
            except Exception as e:
                logger.error(f"OCR failed: {str(e)}")
                state["ocr_result"] = ""
            
            # Combine results
            combined_content = ""
            if state["vision_result"]:
                combined_content += f"Image Analysis: {state['vision_result']}\n\n"
            if state["ocr_result"]:
                combined_content += f"Extracted Text: {state['ocr_result']}\n\n"
            
            state["research_content"] = combined_content
            
        elif input_type == "audio":
            await self._update_step(state, "Transcribing audio...", 3)
            
            try:
                stt_result = await self.stt_agent.execute({
                    "audio_path": file_path
                })
                state["transcription"] = stt_result["transcription"]
                # Update query with transcription
                state["query"] = state["transcription"]
            except Exception as e:
                logger.error(f"STT failed: {str(e)}")
                state["transcription"] = "Failed to transcribe audio"
        
        elif input_type == "document":
            await self._update_step(state, "Processing document...", 3)
            
            try:
                from ..agents.multimodal_agents import DocumentProcessor
                
                if file_path.lower().endswith('.pdf'):
                    content = DocumentProcessor.process_pdf(file_path)
                elif file_path.lower().endswith('.docx'):
                    content = DocumentProcessor.process_docx(file_path)
                elif file_path.lower().endswith('.txt'):
                    content = DocumentProcessor.process_txt(file_path)
                else:
                    content = "Unsupported document format"
                
                # Add to vector store for future retrieval
                chunks = DocumentProcessor.chunk_text(content)
                self.vector_store.add_documents(chunks, [
                    {"source": file_path, "chunk_id": i} for i in range(len(chunks))
                ])
                
                state["research_content"] = content
                
            except Exception as e:
                logger.error(f"Document processing failed: {str(e)}")
                state["research_content"] = f"Failed to process document: {str(e)}"
        
        return state
    
    async def _research(self, state: AgentState) -> AgentState:
        """Conduct research"""
        await self._update_step(state, "Researching information...", 4)
        
        try:
            # Get context from memory
            context = self.memory_manager.get_context(state["session_id"]) or {}
            
            result = await self.research_agent.execute({
                "original_query": state["query"],
                "intent": state["intent"],
                "context": str(context)
            })
            
            state["research_content"] = result["research_content"]
            
        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            state["research_content"] = f"Research failed: {str(e)}"
        
        return state
    
    async def _compare(self, state: AgentState) -> AgentState:
        """Perform comparison"""
        await self._update_step(state, "Comparing entities...", 4)
        
        try:
            result = await self.compare_agent.execute({
                "original_query": state["query"],
                "entities": state["entities"]
            })
            
            state["comparison_result"] = result["comparison_result"]
            state["research_content"] = result["comparison_result"]  # Use for summarization
            
        except Exception as e:
            logger.error(f"Comparison failed: {str(e)}")
            state["comparison_result"] = f"Comparison failed: {str(e)}"
            state["research_content"] = state["comparison_result"]
        
        return state
    
    async def _retrieve(self, state: AgentState) -> AgentState:
        """Retrieve from vector store"""
        await self._update_step(state, "Searching knowledge base...", 4)
        
        try:
            result = await self.retriever_agent.execute({
                "original_query": state["query"]
            })
            
            state["retrieved_content"] = result["retrieved_content"]
            state["research_content"] = result["retrieved_content"]
            
        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            state["retrieved_content"] = f"Retrieval failed: {str(e)}"
            state["research_content"] = state["retrieved_content"]
        
        return state
    
    async def _summarize(self, state: AgentState) -> AgentState:
        """Summarize results"""
        await self._update_step(state, "Analyzing and summarizing...", 5)
        
        try:
            result = await self.summarizer_agent.execute({
                "research_content": state.get("research_content", ""),
                "comparison_result": state.get("comparison_result", ""),
                "target_length": 200
            })
            
            state["summary"] = result["summary"]
            state["key_points"] = result["key_points"]
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            state["summary"] = f"Summarization failed: {str(e)}"
            state["key_points"] = []
        
        return state
    
    async def _critique(self, state: AgentState) -> AgentState:
        """Critique the response quality"""
        await self._update_step(state, "Evaluating response quality...", 6)
        
        try:
            result = await self.critique_agent.execute({
                "original_query": state["query"],
                "summary": state["summary"]
            })
            
            state["quality_score"] = result["quality_score"]
            state["needs_improvement"] = result["needs_improvement"]
            
        except Exception as e:
            logger.error(f"Critique failed: {str(e)}")
            state["quality_score"] = 7.0
            state["needs_improvement"] = False
        
        return state
    
    async def _text_to_speech(self, state: AgentState) -> AgentState:
        """Generate audio if requested"""
        if state.get("enable_tts", False):
            await self._update_step(state, "Generating audio...", 7)
            
            try:
                result = await self.tts_agent.execute({
                    "summary": state["summary"]
                })
                
                state["audio_file"] = result.get("audio_file", "")
                
            except Exception as e:
                logger.error(f"TTS failed: {str(e)}")
                state["audio_file"] = ""
        
        return state
    
    async def _finalize_result(self, state: AgentState) -> AgentState:
        """Finalize and format the result"""
        await self._update_step(state, "Complete", 8)
        
        # Calculate processing time
        processing_time = time.time() - state["start_time"]
        
        # Build final result
        final_result = {
            "query": state["query"],
            "intent": state["intent"],
            "input_type": state["input_type"],
            "research": state.get("research_content", ""),
            "summary": state.get("summary", ""),
            "key_points": state.get("key_points", []),
            "word_count": len(state.get("summary", "").split()),
            "confidence": state.get("confidence", 0.0),
            "quality_score": state.get("quality_score", 0.0),
            "processing_time": processing_time,
            "steps": state["processing_steps"]
        }
        
        # Add multimodal results if available
        if state.get("vision_result"):
            final_result["vision_analysis"] = state["vision_result"]
        if state.get("ocr_result"):
            final_result["extracted_text"] = state["ocr_result"]
        if state.get("transcription"):
            final_result["transcription"] = state["transcription"]
        
        # Add audio if generated
        if state.get("audio_file"):
            final_result["audio"] = {
                "generated": True,
                "file": state["audio_file"],
                "duration": len(state.get("summary", "").split()) * 0.6
            }
        
        state["final_result"] = final_result
        
        # Save to memory
        self.memory_manager.add_to_conversation(state["session_id"], {
            "type": "query",
            "content": state["query"],
            "result": final_result
        })
        
        return state
    
    # Routing functions
    def _route_after_intent(self, state: AgentState) -> str:
        """Route based on intent and input type"""
        input_type = state.get("input_type", "text")
        intent = state.get("intent", "general")
        
        if input_type in ["image", "audio", "document"]:
            return "multimodal"
        elif intent == "compare":
            return "compare"
        elif intent in ["summarize", "research", "explain", "analyze"]:
            # Check if we have documents in vector store
            stats = self.vector_store.get_stats()
            if stats["total_documents"] > 0:
                return "retrieve"
            else:
                return "research"
        else:
            return "research"
    
    def _should_critique(self, state: AgentState) -> str:
        """Decide whether to critique the response"""
        # Only critique if we haven't retried too many times
        if state.get("retry_count", 0) < 2:
            return "critique"
        elif state.get("enable_tts", False):
            return "tts"
        else:
            return "finalize"
    
    def _handle_critique_result(self, state: AgentState) -> str:
        """Handle critique results"""
        if state.get("needs_improvement", False) and state.get("retry_count", 0) < 1:
            state["retry_count"] = state.get("retry_count", 0) + 1
            return "retry"
        elif state.get("enable_tts", False):
            return "tts"
        else:
            return "finalize"
    
    def _should_finalize(self, state: AgentState) -> str:
        """Always finalize after TTS"""
        return "finalize"
    
    async def _update_step(self, state: AgentState, message: str, step: int):
        """Update processing step"""
        step_info = {
            "step": step,
            "message": message,
            "timestamp": time.time(),
            "status": "active" if step < 8 else "completed"
        }
        
        if "processing_steps" not in state:
            state["processing_steps"] = []
        
        state["processing_steps"].append(step_info)
        state["current_step"] = step
        
        # Update session if exists
        if state.get("session_id"):
            session_id = state["session_id"]
            if session_id in self.sessions:
                self.sessions[session_id]["steps"] = state["processing_steps"]
                self.sessions[session_id]["current_step"] = step
    
    async def process_query(self, query: str, session_id: str, enable_tts: bool = False, 
                          file_path: Optional[str] = None) -> Dict[str, Any]:
        """Process a query through the LangGraph workflow"""
        
        # Initialize session tracking
        self.sessions[session_id] = {
            "status": "processing",
            "start_time": time.time(),
            "steps": [],
            "current_step": 0
        }
        
        # Create initial state
        initial_state = AgentState(
            query=query,
            session_id=session_id,
            enable_tts=enable_tts,
            file_path=file_path,
            input_type="text",
            intent="",
            confidence=0.0,
            entities=[],
            context={},
            research_content="",
            comparison_result="",
            vision_result="",
            ocr_result="",
            transcription="",
            retrieved_content="",
            summary="",
            key_points=[],
            quality_score=0.0,
            needs_improvement=False,
            retry_count=0,
            final_result={},
            audio_file=None,
            processing_steps=[],
            start_time=time.time(),
            current_step=0
        )
        
        try:
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Update session
            self.sessions[session_id]["status"] = "completed"
            self.sessions[session_id]["result"] = final_state["final_result"]
            
            return final_state["final_result"]
            
        except Exception as e:
            logger.error(f"LangGraph workflow error: {str(e)}")
            self.sessions[session_id]["status"] = "error"
            self.sessions[session_id]["error"] = str(e)
            raise e
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get session status"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        return self.sessions[session_id]
    
    def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return self.vector_store.get_stats()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return self.memory_manager.get_session_stats()