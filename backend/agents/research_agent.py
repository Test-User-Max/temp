import aiohttp
import json
from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    def __init__(self, config):
        super().__init__("Research Agent", config)
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("original_query", "")
        intent = input_data.get("intent", "general")
        
        # Generate research prompt based on intent
        prompt = self._generate_research_prompt(query, intent)
        
        # Query Ollama
        try:
            response = await self._query_ollama(prompt)
            
            return {
                "research_content": response,
                "source": "mistral_local",
                "confidence": 0.9,
                "word_count": len(response.split())
            }
            
        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            # Fallback response
            return {
                "research_content": f"I apologize, but I'm currently unable to connect to the local Mistral model. Here's what I can tell you about '{query}': This appears to be a query about {intent}. For the most accurate and detailed information, please ensure Ollama is running with the Mistral model loaded.",
                "source": "fallback",
                "confidence": 0.3,
                "word_count": 50
            }
    
    def _generate_research_prompt(self, query: str, intent: str) -> str:
        """Generate appropriate research prompt based on intent"""
        
        prompts = {
            "summarize": f"Provide a comprehensive summary of: {query}. Include key points, main ideas, and important details in a well-structured format.",
            "compare": f"Provide a detailed comparison of: {query}. Include similarities, differences, advantages, and disadvantages in a structured format.",
            "explain": f"Provide a detailed explanation of: {query}. Include definitions, examples, and step-by-step breakdown where applicable.",
            "research": f"Conduct comprehensive research on: {query}. Provide detailed insights, facts, statistics, and relevant information.",
            "analyze": f"Provide a thorough analysis of: {query}. Include context, implications, and detailed examination of the subject.",
            "general": f"Provide detailed and comprehensive information about: {query}. Include relevant facts, context, and insights."
        }
        
        return prompts.get(intent, prompts["general"])
    
    async def _query_ollama(self, prompt: str) -> str:
        """Query Ollama API"""
        url = f"{self.config.ollama_host}/api/generate"
        
        payload = {
            "model": self.config.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"Ollama API error: {response.status}")