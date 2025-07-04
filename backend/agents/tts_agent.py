import pyttsx3
import threading
import os
import tempfile
import shutil
from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class TTSAgent(BaseAgent):
    def __init__(self, config):
        super().__init__("TTS Agent", config)
        self.engine = None
        self._init_tts_engine()
        
    def _init_tts_engine(self):
        """Initialize TTS engine"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.config.tts_rate)
            self.engine.setProperty('volume', self.config.tts_volume)
            
            # Set voice (try to get a pleasant voice)
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    self.engine.setProperty('voice', voices[0].id)
                    
        except Exception as e:
            logger.error(f"TTS initialization failed: {str(e)}")
            self.engine = None
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("summary", "")
        
        if not text:
            return {
                "status": "error",
                "message": "No text to speak",
                "audio_generated": False
            }
        
        if not self.config.tts_enabled or not self.engine:
            return {
                "status": "disabled",
                "message": "TTS is disabled or not available",
                "audio_generated": False
            }
        
        try:
            # Generate audio file
            audio_file = await self._generate_audio(text)
            
            return {
                "status": "success",
                "message": "Audio generated successfully",
                "audio_generated": True,
                "audio_file": audio_file,
                "text_length": len(text),
                "estimated_duration": len(text.split()) * 0.6  # Rough estimate
            }
            
        except Exception as e:
            logger.error(f"TTS generation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"TTS generation failed: {str(e)}",
                "audio_generated": False
            }
    
    async def _generate_audio(self, text: str) -> str:
        """Generate audio file from text"""
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        audio_file = os.path.join(temp_dir, f"tts_output_{hash(text)}.wav")
        
        def speak_to_file():
            try:
                if self.engine is not None:
                    self.engine.save_to_file(text, audio_file)
                    self.engine.runAndWait()
            except Exception as e:
                logger.error(f"Audio generation error: {str(e)}")
                raise e
        
        # Run TTS in separate thread
        thread = threading.Thread(target=speak_to_file)
        thread.start()
        thread.join()
        
        # Copy to static/audio if generated
        if os.path.exists(audio_file):
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            static_audio_dir = os.path.join(BASE_DIR, "static", "audio")
            os.makedirs(static_audio_dir, exist_ok=True)
            dest_file = os.path.join(static_audio_dir, os.path.basename(audio_file))
            shutil.copy(audio_file, dest_file)
            audio_url = f"/audio/{os.path.basename(audio_file)}"
            logger.info(f"TTS audio file copied to: {dest_file}, returning URL: {audio_url}")
            # Return the URL path for frontend
            return audio_url
        logger.error(f"TTS audio file not found after generation: {audio_file}")
        return ""
    
    def speak_text(self, text: str):
        """Speak text directly (for real-time use)"""
        if self.engine:
            def speak():
                if self.engine is not None:
                    self.engine.say(text)
                    self.engine.runAndWait()
            
            thread = threading.Thread(target=speak)
            thread.start()