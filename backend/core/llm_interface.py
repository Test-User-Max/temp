import aiohttp
import json
from typing import Dict, Any, Optional, List
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
import logging

logger = logging.getLogger(__name__)

class OllamaLLM(LLM):
    """Custom Ollama LLM for LangChain integration"""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "mistral", **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.model = model
    
    @property
    def _llm_type(self) -> str:
        return "ollama"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Synchronous call to Ollama"""
        import asyncio
        return asyncio.run(self._acall(prompt, stop, run_manager, **kwargs))
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Asynchronous call to Ollama"""
        url = f"{self.host}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2048)
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        raise Exception(f"Ollama API error: {response.status}")
        except Exception as e:
            logger.error(f"Ollama LLM call failed: {str(e)}")
            raise e

class OllamaVisionLLM(OllamaLLM):
    """Ollama LLM for vision tasks using LLaVA"""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "llava", **kwargs):
        super().__init__(host, model, **kwargs)
    
    async def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail") -> str:
        """Analyze image using LLaVA model"""
        import base64
        
        # Read and encode image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        url = f"{self.host}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 1000
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        raise Exception(f"Ollama Vision API error: {response.status}")
        except Exception as e:
            logger.error(f"Ollama Vision call failed: {str(e)}")
            return f"Error analyzing image: {str(e)}"