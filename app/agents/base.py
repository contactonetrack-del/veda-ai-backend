"""
Base Agent Class
All specialized agents inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from google import genai
from app.core.config import get_settings

settings = get_settings()


class BaseAgent(ABC):
    """Base class for all VEDA AI agents"""
    
    def __init__(self, name: str, description: str, system_prompt: str):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    async def generate(self, user_message: str, context: str = "") -> str:
        """Generate a response using Gemini with agent-specific system prompt"""
        
        full_prompt = f"""{self.system_prompt}

{context}

User: {user_message}

Provide a helpful, accurate response:"""
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return f"I apologize, but I encountered an issue. Please try again."
    
    @abstractmethod
    async def process(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user message and return structured response
        Must be implemented by each specialized agent
        """
        pass
