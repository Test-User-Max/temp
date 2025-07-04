import os
from typing import Dict, Any, List, Optional
from transformers import AutoTokenizer, AutoModel, pipeline
import torch
import pyttsx3
import logging

logger = logging.getLogger(__name__)

class MultilingualService:
    """Comprehensive multilingual support service"""
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi'
        }
        
        self.translation_pipeline = None
        self.language_detection_pipeline = None
        self.tts_engines = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize multilingual models"""
        try:
            # Language detection
            self.language_detection_pipeline = pipeline(
                "text-classification",
                model="facebook/fasttext-language-identification",
                return_all_scores=True
            )
            
            # Translation pipeline
            self.translation_pipeline = pipeline(
                "translation",
                model="facebook/nllb-200-distilled-600M"
            )
            
            logger.info("Multilingual models initialized successfully")
            
        except Exception as e:
            logger.warning(f"Could not initialize multilingual models: {str(e)}")
            # Fallback to basic functionality
            self.language_detection_pipeline = None
            self.translation_pipeline = None
    
    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        if not self.language_detection_pipeline:
            return 'en'  # Default fallback
        
        try:
            results = self.language_detection_pipeline(text)
            if results and len(results) > 0:
                # Get highest confidence language
                best_result = max(results, key=lambda x: x['score'])
                detected_lang = best_result['label']
                
                # Map to our supported languages
                if detected_lang in self.supported_languages:
                    return detected_lang
                
                # Try to map common language codes
                lang_mapping = {
                    'eng': 'en', 'spa': 'es', 'fra': 'fr', 'deu': 'de',
                    'ita': 'it', 'por': 'pt', 'rus': 'ru', 'jpn': 'ja',
                    'kor': 'ko', 'zho': 'zh', 'ara': 'ar', 'hin': 'hi'
                }
                
                return lang_mapping.get(detected_lang, 'en')
            
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
        
        return 'en'  # Default fallback
    
    def translate_text(self, text: str, target_language: str, source_language: str = None) -> str:
        """Translate text to target language"""
        if not self.translation_pipeline:
            return text  # Return original if no translation available
        
        if not source_language:
            source_language = self.detect_language(text)
        
        if source_language == target_language:
            return text  # No translation needed
        
        try:
            # NLLB language codes
            nllb_codes = {
                'en': 'eng_Latn', 'es': 'spa_Latn', 'fr': 'fra_Latn',
                'de': 'deu_Latn', 'it': 'ita_Latn', 'pt': 'por_Latn',
                'ru': 'rus_Cyrl', 'ja': 'jpn_Jpan', 'ko': 'kor_Hang',
                'zh': 'zho_Hans', 'ar': 'ara_Arab', 'hi': 'hin_Deva'
            }
            
            src_code = nllb_codes.get(source_language, 'eng_Latn')
            tgt_code = nllb_codes.get(target_language, 'eng_Latn')
            
            result = self.translation_pipeline(
                text,
                src_lang=src_code,
                tgt_lang=tgt_code
            )
            
            return result[0]['translation_text'] if result else text
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return text
    
    def get_tts_engine(self, language: str = 'en') -> Optional[pyttsx3.Engine]:
        """Get TTS engine for specific language"""
        if language in self.tts_engines:
            return self.tts_engines[language]
        
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            # Language to voice mapping
            voice_mapping = {
                'en': ['english', 'en_', 'en-'],
                'es': ['spanish', 'es_', 'es-'],
                'fr': ['french', 'fr_', 'fr-'],
                'de': ['german', 'de_', 'de-'],
                'it': ['italian', 'it_', 'it-'],
                'pt': ['portuguese', 'pt_', 'pt-'],
                'ru': ['russian', 'ru_', 'ru-'],
                'ja': ['japanese', 'ja_', 'ja-'],
                'ko': ['korean', 'ko_', 'ko-'],
                'zh': ['chinese', 'zh_', 'zh-'],
                'ar': ['arabic', 'ar_', 'ar-'],
                'hi': ['hindi', 'hi_', 'hi-']
            }
            
            # Find appropriate voice
            target_patterns = voice_mapping.get(language, ['english'])
            selected_voice = None
            
            for voice in voices:
                voice_name = voice.name.lower()
                for pattern in target_patterns:
                    if pattern in voice_name:
                        selected_voice = voice.id
                        break
                if selected_voice:
                    break
            
            if selected_voice:
                engine.setProperty('voice', selected_voice)
            
            # Set properties
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.8)
            
            self.tts_engines[language] = engine
            return engine
            
        except Exception as e:
            logger.error(f"TTS engine creation failed for {language}: {str(e)}")
            return None
    
    def speak_text(self, text: str, language: str = 'en') -> bool:
        """Speak text in specified language"""
        engine = self.get_tts_engine(language)
        if not engine:
            return False
        
        try:
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"TTS failed: {str(e)}")
            return False
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages.copy()
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported"""
        return language_code in self.supported_languages

# Global multilingual service
multilingual_service = MultilingualService()