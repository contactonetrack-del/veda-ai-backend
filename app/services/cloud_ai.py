"""
Cloud AI Service - Step 6 (Pro Hybrid Architecture)
Fallback layer for 24/7 availability when laptop is offline.
Uses Groq (speed) and Gemini (utility) free tiers.
"""
import logging
import os
from typing import Dict, Any, Optional, List
import groq
import google.generativeai as genai
from app.core.config import get_settings

settings = get_settings()

class CloudAIService:
    """
    Cloud-based AI service for production parity and 24/7 availability.
    
    This service is used when:
    1. Laptop/Ollama is offline
    2. Fast user experience is prioritized over local privacy
    3. Running in production (Render)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.groq_client = None
        self.gemini_model = None
        
        self._init_groq()
        self._init_gemini()
        
    def _init_groq(self):
        if settings.GROQ_API_KEY:
            try:
                self.groq_client = groq.Groq(api_key=settings.GROQ_API_KEY)
                self.logger.info("Groq Cloud AI initialized")
            except Exception as e:
                self.logger.error(f"Failed to init Groq: {e}")

    def _init_gemini(self):
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.logger.info("Gemini Cloud AI initialized")
            except Exception as e:
                self.logger.error(f"Failed to init Gemini: {e}")

    async def invoke(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_preference: str = "fast",  # "fast" (Groq) or "utility" (Gemini)
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Invoke Cloud AI models with automatic fallback
        """
        
        # Try Groq (Fastest) if preferred or if Gemini is missing
        if (model_preference == "fast" or not self.gemini_model) and self.groq_client:
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return {
                    "success": True,
                    "response": response.choices[0].message.content,
                    "model_used": "groq/llama-3.1-70b",
                    "cloud": True,
                    "cost": "$0 (free tier)"
                }
            except Exception as e:
                self.logger.warning(f"Groq invocation failed, falling back to Gemini: {e}")

        # Fallback to Gemini
        if self.gemini_model:
            try:
                # Merge system prompt if provided
                full_prompt = f"{system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
                response = self.gemini_model.generate_content(full_prompt)
                
                return {
                    "success": True,
                    "response": response.text,
                    "model_used": "gemini-1.5-flash",
                    "cloud": True,
                    "cost": "$0 (free tier)"
                }
            except Exception as e:
                self.logger.error(f"Gemini invocation failed: {e}")
                
        return {
            "success": False,
            "error": "No cloud AI service available. Please check API keys.",
            "cloud": True
        }

    def get_status(self) -> Dict[str, Any]:
        """Check cloud AI availability"""
        return {
            "groq_available": self.groq_client is not None,
            "gemini_available": self.gemini_model is not None,
            "status": "Online" if (self.groq_client or self.gemini_model) else "Offline (Missing Keys)",
            "tier": "Free"
        }

# Singleton instance
cloud_ai_service = CloudAIService()
