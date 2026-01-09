"""
Groq Service
Ultra-fast LLaMA inference using Groq's LPU
Provides fallback and speed options for VEDA AI
"""
from groq import Groq
from typing import Optional
from app.core.config import get_settings

settings = get_settings()


class GroqService:
    """Groq API client for LLaMA models"""
    
    def __init__(self):
        api_key = getattr(settings, 'GROQ_API_KEY', None)
        self.client = Groq(api_key=api_key) if api_key else None
        self.available = self.client is not None
        # Using LLaMA 3 70B for quality, 8B for speed
        self.default_model = "llama3-70b-8192"
        self.fast_model = "llama3-8b-8192"
    
    async def generate_response(
        self, 
        message: str, 
        system_prompt: str = "",
        fast: bool = False
    ) -> str:
        """
        Generate response using Groq LLaMA
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            fast: If True, use smaller faster model
        
        Returns:
            Generated response text
        """
        if not self.available:
            raise Exception("Groq API key not configured")
        
        model = self.fast_model if fast else self.default_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error: {e}")
            raise


# Singleton instance
groq_service = GroqService()
