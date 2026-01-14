import httpx
import logging
from typing import Optional, List, Dict, Any
from app.core.config import get_settings

settings = get_settings()

class OpenRouterService:
    """OpenRouter API client for accessing diverse models"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        self.available = bool(self.api_key)
        
        # High-value models on OpenRouter
        self.reasoning_model = "deepseek/deepseek-r1" # Full 671B model
        self.default_model = "google/gemini-2.0-flash-001"
        self.fast_model = "meta-llama/llama-3.3-70b-instruct"

    async def generate_response(
        self, 
        message: str, 
        system_prompt: str = "", 
        history: list = [],
        model: Optional[str] = None
    ) -> str:
        if not self.available:
            return "Error: OpenRouter API key not configured."

        target_model = model or self.default_model
        
        # Build messages including history
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        for msg in history[-5:]:
            messages.append({"role": msg.get("role"), "content": msg.get("content")})
            
        messages.append({"role": "user", "content": message})
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "HTTP-Referer": "https://veda-ai.com", # Required by OpenRouter
                        "X-Title": "Veda AI",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": target_model,
                        "messages": messages,
                        "temperature": 0.7,
                    }
                )
                
                if response.status_code != 200:
                    self.logger.error(f"OpenRouter Error {response.status_code}: {response.text}")
                    return f"Error: OpenRouter API returned {response.status_code}"
                
                result = response.json()
                if "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"]
                else:
                    return "Error: No response from OpenRouter"
                    
        except Exception as e:
            self.logger.error(f"OpenRouter invocation failed: {str(e)}")
            return f"Error calling OpenRouter: {str(e)}"

# Singleton instance
openrouter_service = OpenRouterService()
