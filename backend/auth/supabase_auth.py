import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

class SupabaseAuth:
    """Supabase-compatible authentication system"""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        # In-memory user store (replace with actual database)
        self.users_db = {}
        self.sessions_db = {}
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def register_user(self, email: str, password: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Register new user"""
        if email in self.users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        user_id = f"user_{len(self.users_db) + 1}"
        hashed_password = self.hash_password(password)
        
        user_data = {
            "id": user_id,
            "email": email,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "preferences": {
                "theme": "dark",
                "language": "en",
                "tts_enabled": False,
                "voice_speed": 150
            }
        }
        
        self.users_db[email] = user_data
        
        # Create tokens
        token_data = {"sub": user_id, "email": email}
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)
        
        return {
            "user": {
                "id": user_id,
                "email": email,
                "metadata": user_data["metadata"],
                "preferences": user_data["preferences"]
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login user"""
        if email not in self.users_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        user_data = self.users_db[email]
        if not self.verify_password(password, user_data["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create tokens
        token_data = {"sub": user_data["id"], "email": email}
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)
        
        return {
            "user": {
                "id": user_data["id"],
                "email": email,
                "metadata": user_data["metadata"],
                "preferences": user_data["preferences"]
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """Get current user from token"""
        payload = self.verify_token(token)
        email = payload.get("email")
        
        if not email or email not in self.users_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        user_data = self.users_db[email]
        return {
            "id": user_data["id"],
            "email": email,
            "metadata": user_data["metadata"],
            "preferences": user_data["preferences"]
        }
    
    async def update_user_preferences(self, email: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences"""
        if email not in self.users_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        self.users_db[email]["preferences"].update(preferences)
        return self.users_db[email]["preferences"]

# Global auth instance
auth_service = SupabaseAuth()

# FastAPI dependency
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """FastAPI dependency to get current user"""
    return await auth_service.get_current_user(credentials.credentials)

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Optional user dependency for public endpoints"""
    if credentials:
        try:
            return await auth_service.get_current_user(credentials.credentials)
        except HTTPException:
            return None
    return None