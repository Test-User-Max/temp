import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        # Ollama Configuration
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
        self.ollama_vision_model = os.getenv("OLLAMA_VISION_MODEL", "llava")
        
        # TTS Configuration
        self.tts_enabled = os.getenv("TTS_ENABLED", "true").lower() == "true"
        self.tts_rate = int(os.getenv("TTS_RATE", "150"))
        self.tts_volume = float(os.getenv("TTS_VOLUME", "0.8"))
        
        # STT Configuration
        self.stt_enabled = os.getenv("STT_ENABLED", "true").lower() == "true"
        self.whisper_model = os.getenv("WHISPER_MODEL", "base")
        
        # Vector Store Configuration
        self.chroma_persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        
        # General Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2048"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.session_timeout = int(os.getenv("SESSION_TIMEOUT", "300"))
        
        # File Upload Configuration
        self.upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
        
        # Memory Configuration
        self.memory_type = os.getenv("MEMORY_TYPE", "file")  # file, redis
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # OCR Configuration
        self.tesseract_path = os.getenv("TESSERACT_PATH", None)