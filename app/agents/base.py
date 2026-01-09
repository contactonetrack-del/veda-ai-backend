"""
Base Agent Class
All specialized agents inherit from this base class
Now uses Model Router for multi-model support with fallback
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Literal
from app.services.model_router import model_router
from app.core.config import get_settings

settings = get_settings()

ModelProvider = Literal["gemini", "groq", "auto"]


class BaseAgent(ABC):
    """Base class for all VEDA AI agents"""
    
    def __init__(self, name: str, description: str, system_prompt: str):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.default_provider: ModelProvider = "auto"
    
    async def generate(
        self, 
        user_message: str, 
        context: str = "",
        provider: ModelProvider = "auto",
        fast: bool = False
    ) -> str:
        """
        Generate a response using model router (multi-provider support)
        
        Args:
            user_message: The user's message
            context: Additional context from memory
            provider: Force specific provider or "auto" for smart routing
            fast: If True, prefer faster models
        
        Returns:
            Generated response text
        """
        
        full_prompt = f"""{context}

User: {user_message}

Provide a helpful, accurate response:"""
        
        try:
            result = await model_router.generate(
                message=full_prompt,
                system_prompt=self.system_prompt,
                provider=provider,
                fast=fast
            )
            
            # Log which model was used
            if result.get("fallback"):
                print(f"[{self.name}] Used fallback: {result.get('provider')}")
            
            return result.get("response", "I apologize, but I encountered an issue.")
            
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return "I apologize, but I encountered an issue. Please try again."
    
    @abstractmethod
    async def process(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user message and return structured response
        Must be implemented by each specialized agent
        """
        pass

