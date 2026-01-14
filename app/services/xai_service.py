import httpx
import logging
from typing import Optional, List, Dict, Any
from app.core.config import get_settings

settings = get_settings()

class XAIService:
    """xAI API client for Grok models"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = settings.XAI_API_KEY
        self.base_url = "https://api.x.ai/v1"
        self.available = bool(self.api_key)
        
        # Models on xAI
        self.default_model = "grok-2-1212"
        self.fast_model = "grok-beta"
        self.reasoning_model = "grok-2-1212"

    async def generate_response(
        self, 
        message: str, 
        system_prompt: str = "", 
        history: list = [],
        model: Optional[str] = None
    ) -> str:
        if not self.available:
            return "Error: xAI API key not configured."

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
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": target_model,
                        "messages": messages,
                        "temperature": 0.7,
                        "stream": False
                    }
                )
                
                if response.status_code != 200:
                    self.logger.error(f"xAI Error {response.status_code}: {response.text}")
                    return f"Error: xAI API returned {response.status_code}"
                
                result = response.json()
                if "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"]
                else:
                    return "Error: No response from xAI"
                    
        except Exception as e:
            self.logger.error(f"xAI invocation failed: {str(e)}")
            return f"Error calling xAI: {str(e)}"

# Singleton instance
xai_service = XAIService()
