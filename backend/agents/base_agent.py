from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import time
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, config):
        self.name = name
        self.config = config
        self.status = "idle"
        self.last_activity = time.time()
        
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return result"""
        pass
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with status tracking"""
        self.status = "running"
        self.last_activity = time.time()
        
        try:
            logger.info(f"{self.name} started processing")
            result = await self.process(input_data)
            self.status = "completed"
            logger.info(f"{self.name} completed processing")
            return result
            
        except Exception as e:
            self.status = "error"
            logger.error(f"{self.name} error: {str(e)}")
            raise e
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "last_activity": self.last_activity
        }