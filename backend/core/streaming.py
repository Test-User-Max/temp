import asyncio
import json
from typing import AsyncGenerator, Dict, Any
from fastapi import Request
from fastapi.responses import StreamingResponse
import logging

logger = logging.getLogger(__name__)

class StreamingService:
    """Service for real-time streaming output"""
    
    def __init__(self):
        self.active_streams = {}
    
    async def create_sse_response(self, session_id: str, generator: AsyncGenerator) -> StreamingResponse:
        """Create Server-Sent Events response"""
        
        async def event_stream():
            try:
                async for data in generator:
                    # Format as SSE
                    if isinstance(data, dict):
                        yield f"data: {json.dumps(data)}\n\n"
                    else:
                        yield f"data: {data}\n\n"
                    
                    # Small delay to prevent overwhelming
                    await asyncio.sleep(0.01)
                    
            except asyncio.CancelledError:
                logger.info(f"Stream cancelled for session {session_id}")
            except Exception as e:
                logger.error(f"Stream error: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            finally:
                # Cleanup
                if session_id in self.active_streams:
                    del self.active_streams[session_id]
                yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"
        
        return StreamingResponse(
            event_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
    
    async def stream_llm_response(self, session_id: str, prompt: str, llm) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream LLM response token by token"""
        try:
            # Start streaming
            yield {
                "type": "stream_start",
                "session_id": session_id,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Simulate token streaming (replace with actual Ollama streaming)
            response = await llm._acall(prompt)
            words = response.split()
            
            accumulated_text = ""
            for i, word in enumerate(words):
                accumulated_text += word + " "
                
                yield {
                    "type": "token",
                    "token": word + " ",
                    "accumulated": accumulated_text.strip(),
                    "progress": (i + 1) / len(words),
                    "session_id": session_id
                }
                
                # Simulate realistic typing speed
                await asyncio.sleep(0.05)
            
            # Final response
            yield {
                "type": "complete",
                "full_response": accumulated_text.strip(),
                "session_id": session_id,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
                "session_id": session_id
            }
    
    async def stream_agent_progress(self, session_id: str, mcp) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream agent execution progress"""
        try:
            # Monitor session progress
            while session_id in mcp.sessions:
                session_data = mcp.sessions[session_id]
                
                yield {
                    "type": "agent_progress",
                    "status": session_data.get("status", "unknown"),
                    "current_step": session_data.get("current_step", 0),
                    "steps": session_data.get("steps", []),
                    "session_id": session_id
                }
                
                if session_data.get("status") in ["completed", "error"]:
                    break
                
                await asyncio.sleep(0.5)
                
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
                "session_id": session_id
            }

# Global streaming service instance
streaming_service = StreamingService()