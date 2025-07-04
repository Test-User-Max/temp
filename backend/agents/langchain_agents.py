from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.tools.base import BaseTool
from typing import Dict, Any, List, Optional, Union
import asyncio
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseLangChainAgent(ABC):
    """Base class for LangChain agents"""
    
    def __init__(self, name: str, llm, config):
        self.name = name
        self.llm = llm
        self.config = config
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    @abstractmethod
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        pass
    
    @abstractmethod
    def _create_agent(self):
        """Create the LangChain agent"""
        pass
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent"""
        try:
            logger.info(f"{self.name} started processing")
            result = await self._process(input_data)
            logger.info(f"{self.name} completed processing")
            return result
        except Exception as e:
            logger.error(f"{self.name} error: {str(e)}")
            raise e
    
    @abstractmethod
    async def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data"""
        pass

class IntentAgent(BaseLangChainAgent):
    """Agent for intent classification using LangChain"""
    
    def _create_tools(self) -> List[Tool]:
        return []  # Intent agent doesn't need tools
    
    def _create_agent(self):
        prompt = PromptTemplate(
            input_variables=["query"],
            template="""
            Analyze the following query and classify its intent. 
            
            Available intents:
            - summarize: User wants a summary of content
            - compare: User wants to compare two or more things
            - explain: User wants an explanation of a concept
            - research: User wants detailed research on a topic
            - read_aloud: User wants text converted to speech
            - analyze: User wants analysis of data or content
            - vision: User wants image analysis
            - general: General question or conversation
            
            Query: {query}
            
            Respond with just the intent name and confidence score (0-1).
            Format: intent_name:confidence_score
            """
        )
        return prompt
    
    async def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("query", "")
        
        try:
            # Use LLM to classify intent
            prompt_text = self.agent.format(query=query)
            response = await self.llm._acall(prompt_text)
            
            # Parse response
            if ":" in response:
                intent, confidence = response.strip().split(":", 1)
                confidence = float(confidence) if confidence.replace(".", "").isdigit() else 0.8
            else:
                intent = response.strip().lower()
                confidence = 0.8
            
            return {
                "intent": intent,
                "confidence": confidence,
                "original_query": query,
                "processed_query": query.lower(),
                "entities": self._extract_entities(query)
            }
            
        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            return {
                "intent": "general",
                "confidence": 0.5,
                "original_query": query,
                "processed_query": query.lower(),
                "entities": []
            }
    
    def _extract_entities(self, query: str) -> List[str]:
        """Simple entity extraction"""
        entities = []
        words = query.split()
        for word in words:
            if word.isupper() or word.istitle():
                entities.append(word)
        return entities

class ResearchAgent(BaseLangChainAgent):
    """Enhanced research agent using LangChain"""
    
    def _create_tools(self) -> List[Tool]:
        return []  # Research agent uses LLM directly
    
    def _create_agent(self):
        prompt = PromptTemplate(
            input_variables=["query", "intent", "context"],
            template="""
            You are a research assistant. Provide comprehensive, accurate information based on the query and intent.
            
            Query: {query}
            Intent: {intent}
            Context: {context}
            
            Provide detailed, well-structured information. Include:
            1. Main concepts and definitions
            2. Key facts and statistics
            3. Different perspectives or approaches
            4. Practical applications or examples
            5. Recent developments or trends
            
            Be thorough but concise. Ensure accuracy and cite reasoning where appropriate.
            """
        )
        return prompt
    
    async def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("original_query", "")
        intent = input_data.get("intent", "general")
        context = input_data.get("context", "")
        
        try:
            prompt_text = self.agent.format(
                query=query,
                intent=intent,
                context=context
            )
            
            response = await self.llm._acall(
                prompt_text,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            return {
                "research_content": response,
                "source": "mistral_local",
                "confidence": 0.9,
                "word_count": len(response.split()),
                "query": query,
                "intent": intent
            }
            
        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            return {
                "research_content": f"I apologize, but I'm currently unable to process your research request: {query}. Please ensure the local LLM is running and try again.",
                "source": "fallback",
                "confidence": 0.3,
                "word_count": 25,
                "query": query,
                "intent": intent
            }

class CompareAgent(BaseLangChainAgent):
    """Agent for comparing entities or concepts"""
    
    def _create_tools(self) -> List[Tool]:
        return []
    
    def _create_agent(self):
        prompt = PromptTemplate(
            input_variables=["query", "entities"],
            template="""
            You are a comparison specialist. Analyze and compare the entities mentioned in the query.
            
            Query: {query}
            Entities to compare: {entities}
            
            Provide a structured comparison including:
            1. Overview of each entity
            2. Key similarities
            3. Key differences
            4. Advantages and disadvantages
            5. Use cases or applications
            6. Conclusion with recommendations
            
            Format the response in a clear, organized manner with headers and bullet points.
            """
        )
        return prompt
    
    async def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("original_query", "")
        entities = input_data.get("entities", [])
        
        try:
            prompt_text = self.agent.format(
                query=query,
                entities=", ".join(entities) if entities else "entities mentioned in the query"
            )
            
            response = await self.llm._acall(prompt_text)
            
            return {
                "comparison_result": response,
                "entities_compared": entities,
                "confidence": 0.9,
                "word_count": len(response.split())
            }
            
        except Exception as e:
            logger.error(f"Comparison failed: {str(e)}")
            return {
                "comparison_result": f"Unable to perform comparison for: {query}",
                "entities_compared": entities,
                "confidence": 0.3,
                "word_count": 10
            }

class SummarizerAgent(BaseLangChainAgent):
    """Enhanced summarizer agent"""
    
    def _create_tools(self) -> List[Tool]:
        return []
    
    def _create_agent(self):
        prompt = PromptTemplate(
            input_variables=["content", "target_length"],
            template="""
            Summarize the following content into a concise, well-structured summary.
            
            Target length: {target_length} words
            Content: {content}
            
            Provide:
            1. A clear, concise summary
            2. Key points (3-5 bullet points)
            3. Main takeaways
            
            Ensure the summary captures the essential information while being easy to understand.
            """
        )
        return prompt
    
    async def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        content = input_data.get("research_content", "") or input_data.get("comparison_result", "")
        target_length = input_data.get("target_length", 150)
        
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
        
        try:
            prompt_text = self.agent.format(
                content=content,
                target_length=target_length
            )
            
            response = await self.llm._acall(prompt_text, temperature=0.3)
            
            return {
                "summary": response,
                "key_points": self._extract_key_points(response),
                "word_count": len(response.split())
            }
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            # Fallback to simple truncation
            words = content.split()
            truncated = " ".join(words[:target_length]) + "..."
            
            return {
                "summary": truncated,
                "key_points": self._extract_key_points(truncated),
                "word_count": len(truncated.split())
            }
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content"""
        sentences = content.split('. ')
        key_points = []
        
        for sentence in sentences[:5]:
            sentence = sentence.strip()
            if len(sentence) > 20:
                key_points.append(sentence)
        
        return key_points

class RetrieverAgent(BaseLangChainAgent):
    """Agent for document retrieval from vector store"""
    
    def __init__(self, name: str, llm, config, vector_store):
        self.vector_store = vector_store
        super().__init__(name, llm, config)
    
    def _create_tools(self) -> List[Tool]:
        return []
    
    def _create_agent(self):
        prompt = PromptTemplate(
            input_variables=["query", "documents"],
            template="""
            Based on the retrieved documents, provide a comprehensive answer to the query.
            
            Query: {query}
            Retrieved Documents: {documents}
            
            Synthesize the information from the documents to provide a complete, accurate answer.
            If the documents don't contain relevant information, state that clearly.
            """
        )
        return prompt
    
    async def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("original_query", "")
        
        try:
            # Search vector store
            search_results = self.vector_store.search(query, n_results=5)
            
            if not search_results:
                return {
                    "retrieved_content": "No relevant documents found in the knowledge base.",
                    "sources": [],
                    "confidence": 0.2
                }
            
            # Format documents for LLM
            documents_text = "\n\n".join([
                f"Document {i+1}: {result['document']}"
                for i, result in enumerate(search_results)
            ])
            
            prompt_text = self.agent.format(
                query=query,
                documents=documents_text
            )
            
            response = await self.llm._acall(prompt_text)
            
            return {
                "retrieved_content": response,
                "sources": [result['metadata'] for result in search_results],
                "confidence": max([result['similarity'] for result in search_results]),
                "num_sources": len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            return {
                "retrieved_content": f"Unable to retrieve relevant information for: {query}",
                "sources": [],
                "confidence": 0.1
            }

class CritiqueAgent(BaseLangChainAgent):
    """Agent for evaluating and critiquing responses"""
    
    def _create_tools(self) -> List[Tool]:
        return []
    
    def _create_agent(self):
        prompt = PromptTemplate(
            input_variables=["query", "response", "criteria"],
            template="""
            Evaluate the quality of the response to the given query based on the criteria.
            
            Query: {query}
            Response: {response}
            Evaluation Criteria: {criteria}
            
            Provide:
            1. Overall quality score (0-10)
            2. Strengths of the response
            3. Areas for improvement
            4. Specific suggestions for enhancement
            5. Whether the response adequately answers the query (Yes/No)
            
            Be objective and constructive in your evaluation.
            """
        )
        return prompt
    
    async def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("original_query", "")
        response = input_data.get("summary", "") or input_data.get("research_content", "")
        
        criteria = [
            "Accuracy and factual correctness",
            "Completeness of the answer",
            "Clarity and readability",
            "Relevance to the query",
            "Proper structure and organization"
        ]
        
        try:
            prompt_text = self.agent.format(
                query=query,
                response=response,
                criteria="; ".join(criteria)
            )
            
            evaluation = await self.llm._acall(prompt_text, temperature=0.2)
            
            # Extract quality score (simple parsing)
            quality_score = 7.5  # Default score
            if "score" in evaluation.lower():
                import re
                score_match = re.search(r'(\d+(?:\.\d+)?)', evaluation)
                if score_match:
                    quality_score = float(score_match.group(1))
                    if quality_score > 10:
                        quality_score = quality_score / 10  # Normalize if out of 10
            
            return {
                "evaluation": evaluation,
                "quality_score": quality_score,
                "needs_improvement": quality_score < 6.0,
                "criteria_used": criteria
            }
            
        except Exception as e:
            logger.error(f"Critique failed: {str(e)}")
            return {
                "evaluation": "Unable to evaluate response quality",
                "quality_score": 5.0,
                "needs_improvement": False,
                "criteria_used": criteria
            }