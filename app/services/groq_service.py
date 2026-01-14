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
        
        # Phase 3: Zero-Cost Models (2026)
        # DeepSeek R1 Distill: 1000 req/day free (High Reasoning)
        # Note: Rollback to Llama 3.3 70B due to DeepSeek availability on free tier
        self.reasoning_model = "llama-3.3-70b-versatile"
        
        # Llama 3.3 70B: 14.4k req/day free (General Purpose)
        self.default_model = "llama-3.3-70b-versatile"
        
        # Llama 3.1 8B: Low latency (Fast Chat)
        self.fast_model = "llama-3.1-8b-instant"
    
    async def generate_response(
        self, 
        message: str, 
        system_prompt: str = "",
        history: list = [],
        fast: bool = False,
        model: Optional[str] = None
    ) -> str:
        """
        Generate response using Groq LLaMA or DeepSeek
        """
        if not self.available:
            raise Exception("Groq API key not configured")
        
        # Use provided model, or fallback to fast/default selection
        if not model:
            model = self.fast_model if fast else self.default_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        # Append history
        for msg in history:
            role = "user" if msg.get("role") == "user" else "assistant"
            content = msg.get("content", "")
            if content:
                messages.append({"role": role, "content": content})
                
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
