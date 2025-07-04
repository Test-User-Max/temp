import redis
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RedisMemoryManager:
    """Enhanced memory management with Redis support"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = None
        self.fallback_memory = {}  # Fallback to in-memory if Redis unavailable
        self.use_redis = False
        
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            self.use_redis = True
            logger.info("Redis memory manager initialized successfully")
        except Exception as e:
            logger.warning(f"Redis not available, using fallback memory: {str(e)}")
            self.use_redis = False
    
    def set_user_memory(self, user_id: str, key: str, value: Any, expire_hours: int = 24):
        """Set user-specific memory with expiration"""
        memory_key = f"user:{user_id}:memory:{key}"
        
        try:
            if self.use_redis:
                self.redis_client.setex(
                    memory_key,
                    timedelta(hours=expire_hours),
                    json.dumps(value, default=str)
                )
            else:
                # Fallback storage
                if user_id not in self.fallback_memory:
                    self.fallback_memory[user_id] = {}
                self.fallback_memory[user_id][key] = {
                    "value": value,
                    "expires_at": datetime.utcnow() + timedelta(hours=expire_hours)
                }
        except Exception as e:
            logger.error(f"Failed to set user memory: {str(e)}")
    
    def get_user_memory(self, user_id: str, key: str) -> Any:
        """Get user-specific memory"""
        memory_key = f"user:{user_id}:memory:{key}"
        
        try:
            if self.use_redis:
                value = self.redis_client.get(memory_key)
                return json.loads(value) if value else None
            else:
                # Fallback storage
                if user_id in self.fallback_memory and key in self.fallback_memory[user_id]:
                    memory_item = self.fallback_memory[user_id][key]
                    if datetime.utcnow() < memory_item["expires_at"]:
                        return memory_item["value"]
                    else:
                        # Expired, remove it
                        del self.fallback_memory[user_id][key]
                return None
        except Exception as e:
            logger.error(f"Failed to get user memory: {str(e)}")
            return None
    
    def add_conversation_history(self, user_id: str, session_id: str, message: Dict[str, Any]):
        """Add message to conversation history"""
        history_key = f"user:{user_id}:conversation:{session_id}"
        
        try:
            message["timestamp"] = datetime.utcnow().isoformat()
            
            if self.use_redis:
                # Use Redis list for conversation history
                self.redis_client.lpush(history_key, json.dumps(message, default=str))
                # Keep only last 100 messages
                self.redis_client.ltrim(history_key, 0, 99)
                # Set expiration for the entire conversation
                self.redis_client.expire(history_key, timedelta(days=7))
            else:
                # Fallback storage
                if user_id not in self.fallback_memory:
                    self.fallback_memory[user_id] = {}
                if f"conversation:{session_id}" not in self.fallback_memory[user_id]:
                    self.fallback_memory[user_id][f"conversation:{session_id}"] = []
                
                self.fallback_memory[user_id][f"conversation:{session_id}"].insert(0, message)
                # Keep only last 100 messages
                self.fallback_memory[user_id][f"conversation:{session_id}"] = \
                    self.fallback_memory[user_id][f"conversation:{session_id}"][:100]
                    
        except Exception as e:
            logger.error(f"Failed to add conversation history: {str(e)}")
    
    def get_conversation_history(self, user_id: str, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history"""
        history_key = f"user:{user_id}:conversation:{session_id}"
        
        try:
            if self.use_redis:
                messages = self.redis_client.lrange(history_key, 0, limit - 1)
                return [json.loads(msg) for msg in messages]
            else:
                # Fallback storage
                if user_id in self.fallback_memory and f"conversation:{session_id}" in self.fallback_memory[user_id]:
                    return self.fallback_memory[user_id][f"conversation:{session_id}"][:limit]
                return []
        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            return []
    
    def set_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Set user preferences"""
        prefs_key = f"user:{user_id}:preferences"
        
        try:
            if self.use_redis:
                self.redis_client.set(prefs_key, json.dumps(preferences, default=str))
                # Preferences don't expire
            else:
                # Fallback storage
                if user_id not in self.fallback_memory:
                    self.fallback_memory[user_id] = {}
                self.fallback_memory[user_id]["preferences"] = preferences
        except Exception as e:
            logger.error(f"Failed to set user preferences: {str(e)}")
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        prefs_key = f"user:{user_id}:preferences"
        
        try:
            if self.use_redis:
                prefs = self.redis_client.get(prefs_key)
                return json.loads(prefs) if prefs else {}
            else:
                # Fallback storage
                if user_id in self.fallback_memory and "preferences" in self.fallback_memory[user_id]:
                    return self.fallback_memory[user_id]["preferences"]
                return {}
        except Exception as e:
            logger.error(f"Failed to get user preferences: {str(e)}")
            return {}
    
    def cache_agent_result(self, cache_key: str, result: Any, expire_minutes: int = 30):
        """Cache agent results for performance"""
        try:
            if self.use_redis:
                self.redis_client.setex(
                    f"cache:{cache_key}",
                    timedelta(minutes=expire_minutes),
                    json.dumps(result, default=str)
                )
            else:
                # Simple in-memory cache
                if "cache" not in self.fallback_memory:
                    self.fallback_memory["cache"] = {}
                self.fallback_memory["cache"][cache_key] = {
                    "value": result,
                    "expires_at": datetime.utcnow() + timedelta(minutes=expire_minutes)
                }
        except Exception as e:
            logger.error(f"Failed to cache result: {str(e)}")
    
    def get_cached_result(self, cache_key: str) -> Any:
        """Get cached agent result"""
        try:
            if self.use_redis:
                cached = self.redis_client.get(f"cache:{cache_key}")
                return json.loads(cached) if cached else None
            else:
                # Check in-memory cache
                if "cache" in self.fallback_memory and cache_key in self.fallback_memory["cache"]:
                    cache_item = self.fallback_memory["cache"][cache_key]
                    if datetime.utcnow() < cache_item["expires_at"]:
                        return cache_item["value"]
                    else:
                        del self.fallback_memory["cache"][cache_key]
                return None
        except Exception as e:
            logger.error(f"Failed to get cached result: {str(e)}")
            return None
    
    def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all session IDs for a user"""
        try:
            if self.use_redis:
                pattern = f"user:{user_id}:conversation:*"
                keys = self.redis_client.keys(pattern)
                return [key.split(":")[-1] for key in keys]
            else:
                # Fallback storage
                if user_id in self.fallback_memory:
                    sessions = []
                    for key in self.fallback_memory[user_id].keys():
                        if key.startswith("conversation:"):
                            sessions.append(key.replace("conversation:", ""))
                    return sessions
                return []
        except Exception as e:
            logger.error(f"Failed to get user sessions: {str(e)}")
            return []
    
    def cleanup_expired_data(self):
        """Cleanup expired data (mainly for fallback storage)"""
        if not self.use_redis:
            try:
                current_time = datetime.utcnow()
                for user_id in list(self.fallback_memory.keys()):
                    if user_id == "cache":
                        # Clean cache
                        for cache_key in list(self.fallback_memory["cache"].keys()):
                            if current_time >= self.fallback_memory["cache"][cache_key]["expires_at"]:
                                del self.fallback_memory["cache"][cache_key]
                    else:
                        # Clean user memory
                        user_data = self.fallback_memory[user_id]
                        for key in list(user_data.keys()):
                            if isinstance(user_data[key], dict) and "expires_at" in user_data[key]:
                                if current_time >= user_data[key]["expires_at"]:
                                    del user_data[key]
            except Exception as e:
                logger.error(f"Failed to cleanup expired data: {str(e)}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        try:
            if self.use_redis:
                info = self.redis_client.info()
                return {
                    "type": "redis",
                    "connected": True,
                    "memory_used": info.get("used_memory_human", "unknown"),
                    "total_keys": self.redis_client.dbsize()
                }
            else:
                return {
                    "type": "fallback",
                    "connected": False,
                    "total_users": len([k for k in self.fallback_memory.keys() if k != "cache"]),
                    "cache_entries": len(self.fallback_memory.get("cache", {}))
                }
        except Exception as e:
            logger.error(f"Failed to get memory stats: {str(e)}")
            return {"type": "unknown", "connected": False, "error": str(e)}

# Global enhanced memory manager
enhanced_memory = RedisMemoryManager()