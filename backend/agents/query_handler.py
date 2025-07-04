import re
from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class QueryHandlerAgent(BaseAgent):
    def __init__(self, config):
        super().__init__("Query Handler", config)
        self.intent_patterns = {
            "summarize": [r"summarize", r"summary", r"brief", r"overview"],
            "compare": [r"compare", r"vs", r"versus", r"difference", r"contrast"],
            "explain": [r"explain", r"what is", r"how does", r"why"],
            "research": [r"research", r"find", r"information", r"details"],
            "read_aloud": [r"read", r"speak", r"say", r"voice", r"audio"],
            "analyze": [r"analyze", r"analysis", r"examine", r"study"]
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("query", "").lower()
        
        # Extract intent using pattern matching
        intent = self._extract_intent(query)
        
        # Extract entities (simple keyword extraction)
        entities = self._extract_entities(query)
        
        # Determine complexity
        complexity = self._assess_complexity(query)
        
        return {
            "intent": intent,
            "entities": entities,
            "complexity": complexity,
            "original_query": input_data.get("query", ""),
            "processed_query": query,
            "confidence": 0.8  # Simple confidence score
        }
    
    def _extract_intent(self, query: str) -> str:
        """Extract intent from query using pattern matching"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    return intent
        return "general"
    
    def _extract_entities(self, query: str) -> list:
        """Simple entity extraction"""
        entities = []
        
        # Extract potential entities (simple approach)
        words = query.split()
        for word in words:
            if word.isupper() or word.istitle():
                entities.append(word)
        
        return entities
    
    def _assess_complexity(self, query: str) -> str:
        """Assess query complexity"""
        word_count = len(query.split())
        
        if word_count < 5:
            return "simple"
        elif word_count < 15:
            return "medium"
        else:
            return "complex"