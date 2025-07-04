import os
import tempfile
import shutil
from typing import Dict, Any, Optional
import logging
import asyncio
from PIL import Image
import pytesseract
import whisper
import soundfile as sf
import numpy as np
from .langchain_agents import BaseLangChainAgent
from ..core.llm_interface import OllamaVisionLLM

logger = logging.getLogger(__name__)

class VisionAgent(BaseLangChainAgent):
    """Agent for image analysis using LLaVA"""
    
    def __init__(self, name: str, llm, config):
        self.vision_llm = OllamaVisionLLM(
            host=config.ollama_host,
            model=config.ollama_vision_model
        )
        super().__init__(name, llm, config)
    
    def _create_tools(self):
        return []
    
    def _create_agent(self):
        return None  # Vision agent uses specialized LLM
    
    async def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        image_path = input_data.get("image_path", "")
        prompt = input_data.get("prompt", "Describe this image in detail")
        
        if not image_path or not os.path.exists(image_path):
            return {
                "vision_result": "No valid image provided",
                "confidence": 0.0,
                "image_path": image_path
            }
        
        try:
            # Analyze image with LLaVA
            description = await self.vision_llm.analyze_image(image_path, prompt)
            
            # Get image metadata
            with Image.open(image_path) as img:
                width, height = img.size
                format_type = img.format
            
            return {
                "vision_result": description,
                "confidence": 0.9,
                "image_path": image_path,
                "image_metadata": {
                    "width": width,
                    "height": height,
                    "format": format_type
                }
            }
            
        except Exception as e:
            logger.error(f"Vision analysis failed: {str(e)}")
            return {
                "vision_result": f"Failed to analyze image: {str(e)}",
                "confidence": 0.1,
                "image_path": image_path
            }

class OCRAgent(BaseLangChainAgent):
    """Agent for text extraction from images using Tesseract"""
    
    def _create_tools(self):
        return []
    
    def _create_agent(self):
        return None
    
    async def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        image_path = input_data.get("image_path", "")
        
        if not image_path or not os.path.exists(image_path):
            return {
                "ocr_result": "No valid image provided",
                "confidence": 0.0,
                "text_blocks": []
            }
        
        try:
            # Configure Tesseract if path is provided
            if self.config.tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_path
            
            # Extract text from image
            image = Image.open(image_path)
            
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Extract text
            extracted_text = pytesseract.image_to_string(image)
            
            # Process text blocks with confidence scores
            text_blocks = []
            for i in range(len(ocr_data['text'])):
                if int(ocr_data['conf'][i]) > 30:  # Filter low confidence text
                    text_blocks.append({
                        'text': ocr_data['text'][i],
                        'confidence': int(ocr_data['conf'][i]),
                        'bbox': {
                            'x': ocr_data['left'][i],
                            'y': ocr_data['top'][i],
                            'width': ocr_data['width'][i],
                            'height': ocr_data['height'][i]
                        }
                    })
            
            # Calculate overall confidence
            confidences = [block['confidence'] for block in text_blocks if block['text'].strip()]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "ocr_result": extracted_text.strip(),
                "confidence": avg_confidence / 100,  # Normalize to 0-1
                "text_blocks": text_blocks,
                "total_blocks": len(text_blocks)
            }
            
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            return {
                "ocr_result": f"OCR extraction failed: {str(e)}",
                "confidence": 0.0,
                "text_blocks": []
            }

class STTAgent(BaseLangChainAgent):
    """Agent for speech-to-text using Whisper"""
    
    def __init__(self, name: str, llm, config):
        super().__init__(name, llm, config)
        self.whisper_model = None
        self._load_whisper_model()
    
    def _load_whisper_model(self):
        """Load Whisper model"""
        try:
            self.whisper_model = whisper.load_model(self.config.whisper_model)
            logger.info(f"Loaded Whisper model: {self.config.whisper_model}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
    
    def _create_tools(self):
        return []
    
    def _create_agent(self):
        return None
    
    async def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        audio_path = input_data.get("audio_path", "")
        
        if not audio_path or not os.path.exists(audio_path):
            return {
                "transcription": "No valid audio file provided",
                "confidence": 0.0,
                "language": "unknown"
            }
        
        if not self.whisper_model:
            return {
                "transcription": "Whisper model not available",
                "confidence": 0.0,
                "language": "unknown"
            }
        
        try:
            # Transcribe audio
            result = self.whisper_model.transcribe(audio_path)
            
            return {
                "transcription": result["text"].strip(),
                "confidence": 0.9,  # Whisper doesn't provide confidence scores
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", [])
            }
            
        except Exception as e:
            logger.error(f"STT failed: {str(e)}")
            return {
                "transcription": f"Speech transcription failed: {str(e)}",
                "confidence": 0.0,
                "language": "unknown"
            }

class TTSAgent(BaseLangChainAgent):
    """Enhanced TTS agent with better voice control"""
    
    def __init__(self, name: str, llm, config):
        super().__init__(name, llm, config)
        self.engine = None
        self._init_tts_engine()
    
    def _init_tts_engine(self):
        """Initialize TTS engine"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.config.tts_rate)
            self.engine.setProperty('volume', self.config.tts_volume)
            
            # Set voice preferences
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    self.engine.setProperty('voice', voices[0].id)
                    
        except Exception as e:
            logger.error(f"TTS initialization failed: {str(e)}")
            self.engine = None
    
    def _create_tools(self):
        return []
    
    def _create_agent(self):
        return None
    
    async def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get("summary", "") or input_data.get("text", "")
        
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
                "estimated_duration": len(text.split()) * 0.6
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
        import threading
        thread = threading.Thread(target=speak_to_file)
        thread.start()
        thread.join()
        
        # Copy to static/audio if generated
        if os.path.exists(audio_file):
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            static_audio_dir = os.path.join(BASE_DIR, "static", "audio")
            os.makedirs(static_audio_dir, exist_ok=True)
            dest_file = os.path.join(static_audio_dir, os.path.basename(audio_file))
            shutil.copy(audio_file, dest_file)
            audio_url = f"/audio/{os.path.basename(audio_file)}"
            logger.info(f"TTS audio file copied to: {dest_file}, returning URL: {audio_url}")
            return audio_url
        
        logger.error(f"TTS audio file not found after generation: {audio_file}")
        return ""

class DocumentProcessor:
    """Utility class for processing various document types"""
    
    @staticmethod
    def process_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"PDF processing failed: {str(e)}")
            return f"Failed to process PDF: {str(e)}"
    
    @staticmethod
    def process_docx(file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX processing failed: {str(e)}")
            return f"Failed to process DOCX: {str(e)}"
    
    @staticmethod
    def process_txt(file_path: str) -> str:
        """Read text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"TXT processing failed: {str(e)}")
            return f"Failed to process TXT: {str(e)}"
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
        """Split text into chunks for vector storage"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + chunk_size - 200, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks