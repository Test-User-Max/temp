import aiohttp
from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class SummarizerAgent(BaseAgent):
    def __init__(self, config):
        super().__init__("Summarizer Agent", config)
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        content = input_data.get("research_content", "")
        
        if not content:
            return {
                "summary": "No content to summarize",
                "key_points": [],
                "word_count": 0
            }
        
        # If content is already short, return as is
        if len(content.split()) < 100:
            return {
                "summary": content,
                "key_points": self._extract_key_points(content),
                "word_count": len(content.split())
            }
        
        # Generate summary using Ollama
        try:
            summary = await self._generate_summary(content)
            key_points = self._extract_key_points(summary)
            
            return {
                "summary": summary,
                "key_points": key_points,
                "word_count": len(summary.split())
            }
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            # Fallback to simple truncation
            words = content.split()
            truncated = " ".join(words[:150]) + "..."
            
            return {
                "summary": truncated,
                "key_points": self._extract_key_points(truncated),
                "word_count": len(truncated.split())
            }
    
    async def _generate_summary(self, content: str) -> str:
        """Generate summary using Ollama"""
        prompt = f"Please provide a concise summary of the following content. Focus on the main points and key insights:\n\n{content}"
        
        url = f"{self.config.ollama_host}/api/generate"
        
        payload = {
            "model": self.config.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more focused summaries
                "num_predict": 500   # Limit summary length
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"Ollama API error: {response.status}")
    
    def _extract_key_points(self, content: str) -> list:
        """Extract key points from content"""
        sentences = content.split('. ')
        key_points = []
        
        for sentence in sentences[:5]:  # Limit to 5 key points
            sentence = sentence.strip()
            if len(sentence) > 20:  # Filter out very short sentences
                key_points.append(sentence)
        
        return key_points