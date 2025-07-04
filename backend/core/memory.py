import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """Memory manager for session and context management"""
    
    def __init__(self, memory_type: str = "file", storage_path: str = "./data/memory"):
        self.memory_type = memory_type
        self.storage_path = storage_path
        self.sessions = {}
        
        if memory_type == "file":
            os.makedirs(storage_path, exist_ok=True)
            self._load_sessions()
    
    def _load_sessions(self):
        """Load sessions from file storage"""
        try:
            session_file = os.path.join(self.storage_path, "sessions.json")
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    self.sessions = json.load(f)
                logger.info(f"Loaded {len(self.sessions)} sessions from storage")
        except Exception as e:
            logger.error(f"Failed to load sessions: {str(e)}")
            self.sessions = {}
    
    def _save_sessions(self):
        """Save sessions to file storage"""
        try:
            session_file = os.path.join(self.storage_path, "sessions.json")
            with open(session_file, 'w') as f:
                json.dump(self.sessions, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save sessions: {str(e)}")
    
    def create_session(self, session_id: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new session"""
        session = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "conversation_history": [],
            "context": {},
            "user_data": user_data or {},
            "preferences": {
                "tts_enabled": False,
                "voice_speed": 150,
                "theme": "dark"
            }
        }
        
        self.sessions[session_id] = session
        self._save_sessions()
        
        logger.info(f"Created session: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        if session:
            # Update last activity
            session["last_activity"] = datetime.now().isoformat()
            self._save_sessions()
        return session
    
    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)
            self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
            self._save_sessions()
    
    def add_to_conversation(self, session_id: str, message: Dict[str, Any]):
        """Add message to conversation history"""
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        message["timestamp"] = datetime.now().isoformat()
        self.sessions[session_id]["conversation_history"].append(message)
        self.sessions[session_id]["last_activity"] = datetime.now().isoformat()
        self._save_sessions()
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for session"""
        session = self.get_session(session_id)
        if session:
            return session["conversation_history"][-limit:]
        return []
    
    def set_context(self, session_id: str, key: str, value: Any):
        """Set context variable for session"""
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        self.sessions[session_id]["context"][key] = value
        self._save_sessions()
    
    def get_context(self, session_id: str, key: str = None):
        """Get context for session"""
        session = self.get_session(session_id)
        if session:
            if key:
                return session["context"].get(key)
            return session["context"]
        return None
    
    def cleanup_old_sessions(self, days: int = 7):
        """Clean up sessions older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            last_activity = datetime.fromisoformat(session["last_activity"])
            if last_activity < cutoff_date:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self._save_sessions()
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        total_sessions = len(self.sessions)
        total_messages = sum(len(session["conversation_history"]) for session in self.sessions.values())
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "memory_type": self.memory_type
        }