import asyncio
import time
from typing import Dict, Any, Optional
from .query_handler import QueryHandlerAgent
from .research_agent import ResearchAgent
from .summarizer_agent import SummarizerAgent
from .tts_agent import TTSAgent
import logging

logger = logging.getLogger(__name__)

class MultiAgentControlPlane:
    def __init__(self, query_handler: QueryHandlerAgent, research_agent: ResearchAgent, 
                 summarizer_agent: SummarizerAgent, tts_agent: TTSAgent, config):
        self.query_handler = query_handler
        self.research_agent = research_agent
        self.summarizer_agent = summarizer_agent
        self.tts_agent = tts_agent
        self.config = config
        self.sessions = {}
        self.active_tasks = {}
        
    async def process_query(self, query: str, session_id: str, enable_tts: bool = False) -> Dict[str, Any]:
        """Process a query through the multi-agent pipeline"""
        
        # Initialize session
        self.sessions[session_id] = {
            "status": "processing",
            "start_time": time.time(),
            "steps": [],
            "current_step": 0
        }
        
        try:
            # Step 1: Query Handler
            await self._update_session_step(session_id, "Understanding your query...", 1)
            
            handler_result = await self.query_handler.execute({
                "query": query,
                "session_id": session_id
            })
            
            # Step 2: Research Agent
            await self._update_session_step(session_id, "Researching information...", 2)
            
            research_result = await self.research_agent.execute(handler_result)
            
            # Step 3: Summarizer Agent
            await self._update_session_step(session_id, "Analyzing and summarizing...", 3)
            
            summary_result = await self.summarizer_agent.execute(research_result)
            
            # Step 4: TTS Agent (if enabled)
            tts_result = None
            if enable_tts:
                await self._update_session_step(session_id, "Generating audio...", 4)
                tts_result = await self.tts_agent.execute(summary_result)
            
            # Complete session
            await self._update_session_step(session_id, "Complete", 5)
            
            # Compile final result
            final_result = {
                "query": query,
                "intent": handler_result.get("intent"),
                "research": research_result.get("research_content"),
                "summary": summary_result.get("summary"),
                "key_points": summary_result.get("key_points", []),
                "word_count": summary_result.get("word_count", 0),
                "confidence": research_result.get("confidence", 0.0),
                "processing_time": time.time() - self.sessions[session_id]["start_time"],
                "steps": self.sessions[session_id]["steps"]
            }
            
            if tts_result:
                final_result["audio"] = {
                    "generated": tts_result.get("audio_generated", False),
                    "file": tts_result.get("audio_file"),
                    "duration": tts_result.get("estimated_duration", 0)
                }
            
            self.sessions[session_id]["status"] = "completed"
            self.sessions[session_id]["result"] = final_result
            
            return final_result
            
        except Exception as e:
            logger.error(f"MCP processing error: {str(e)}")
            self.sessions[session_id]["status"] = "error"
            self.sessions[session_id]["error"] = str(e)
            raise e
    
    async def _update_session_step(self, session_id: str, message: str, step: int):
        """Update session step"""
        if session_id in self.sessions:
            self.sessions[session_id]["steps"].append({
                "step": step,
                "message": message,
                "timestamp": time.time(),
                "status": "active" if step < 5 else "completed"
            })
            self.sessions[session_id]["current_step"] = step
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get session status"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        return self.sessions[session_id]
    
    async def cancel_session(self, session_id: str) -> Dict[str, Any]:
        """Cancel a session"""
        if session_id in self.sessions:
            self.sessions[session_id]["status"] = "cancelled"
            return {"message": "Session cancelled"}
        
        return {"error": "Session not found"}
    
    def cleanup_old_sessions(self):
        """Clean up old sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            if current_time - session_data["start_time"] > self.config.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")