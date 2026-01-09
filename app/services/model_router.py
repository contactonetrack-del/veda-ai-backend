"""
Model Router
Intelligently routes requests to the best available model
Provides fallback and load balancing across providers
"""
from typing import Optional, Literal
from app.services.gemini import gemini_service
from app.services.groq_service import groq_service
from app.core.config import get_settings

settings = get_settings()

ModelProvider = Literal["gemini", "groq", "auto"]


class ModelRouter:
    """Routes requests to the best available AI model"""
    
    def __init__(self):
        self.providers = {
            "gemini": gemini_service,
            "groq": groq_service
        }
        # Priority order for fallback
        self.priority = ["gemini", "groq"]
    
    def get_available_models(self) -> list:
        """Return list of available model providers"""
        available = []
        if True:  # Gemini always configured
            available.append("gemini")
        if groq_service.available:
            available.append("groq")
        return available
    
    async def generate(
        self,
        message: str,
        system_prompt: str = "",
        provider: ModelProvider = "auto",
        fast: bool = False
    ) -> dict:
        """
        Generate response using the best available model
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            provider: Force specific provider or "auto" for smart routing
            fast: If True, prefer faster models
        
        Returns:
            Dict with response and metadata
        """
        
        # Auto routing logic
        if provider == "auto":
            # Use Groq if available and fast mode requested (LLaMA is faster)
            if fast and groq_service.available:
                provider = "groq"
            else:
                provider = "gemini"
        
        # Try primary provider
        try:
            if provider == "groq" and groq_service.available:
                response = await groq_service.generate_response(
                    message, 
                    system_prompt, 
                    fast=fast
                )
                return {
                    "response": response,
                    "provider": "groq",
                    "model": groq_service.fast_model if fast else groq_service.default_model,
                    "fallback": False
                }
            else:
                # Default to Gemini
                full_prompt = f"{system_prompt}\n\n{message}" if system_prompt else message
                response = await gemini_service.generate_response(full_prompt)
                return {
                    "response": response,
                    "provider": "gemini",
                    "model": "gemini-2.0-flash-exp",
                    "fallback": False
                }
        
        except Exception as e:
            print(f"Primary provider {provider} failed: {e}")
            
            # Fallback to other provider
            fallback_provider = "groq" if provider == "gemini" else "gemini"
            
            try:
                if fallback_provider == "groq" and groq_service.available:
                    response = await groq_service.generate_response(message, system_prompt)
                    return {
                        "response": response,
                        "provider": "groq",
                        "model": groq_service.default_model,
                        "fallback": True
                    }
                else:
                    full_prompt = f"{system_prompt}\n\n{message}" if system_prompt else message
                    response = await gemini_service.generate_response(full_prompt)
                    return {
                        "response": response,
                        "provider": "gemini",
                        "model": "gemini-2.0-flash-exp",
                        "fallback": True
                    }
            except Exception as fallback_error:
                print(f"Fallback also failed: {fallback_error}")
                return {
                    "response": "I apologize, but I'm having trouble connecting to my AI services. Please try again in a moment.",
                    "provider": "none",
                    "model": "none",
                    "fallback": True,
                    "error": str(fallback_error)
                }


# Singleton instance
model_router = ModelRouter()
