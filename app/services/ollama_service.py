"""
Ollama Cloud Service - Phase 2 (Cloud Native)
Manages connection to Ollama Cloud API (ollama.com)
Provides access to DeepSeek R1 and other open models via cloud.
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()


try:
    import ollama
    OLLAMA_LIB_AVAILABLE = True
except ImportError:
    OLLAMA_LIB_AVAILABLE = False
    logging.warning("Ollama library not installed. Run: pip install ollama")

# Note: removing Cloud AI fallback import to avoid circular dependency loop if this BECOMES a primary cloud service.
# If this fails, the Router should handle fallback to OpenAI/Gemini.


class OllamaCloudService:
    """
    Ollama Cloud Service
    Connects to Ollama Cloud API for reasoning and open models.
    
    Models (Cloud):
    - reasoning: DeepSeek-R1 (Best-in-class reasoning)
    - vision: Llama 3.2 Vision
    - fast: Phi-4 / Llama 3
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Model configuration (Next-Gen Cloud Models)
        self.models = {
            "reasoning": "deepseek-v3.1:671b",    # Massive 671B reasoning model
            "vision": "gemini-3-flash-preview",   # Next-Gen Vision
            "fast": "gpt-oss:20b",                # Low latency
            "coding": "qwen3-coder:480b",         # Specialized coding giant
            "general": "gpt-oss:120b",            # Balanced powerhouse
        }
        
        # Fallback models if primary not available
        self.fallback_models = {
            "reasoning": "qwen2.5:7b",
            "vision": "llama3.2:latest",
            "fast": "phi:latest",
            "coding": "deepseek-r1:7b",
        }
        
        self.is_available = OLLAMA_LIB_AVAILABLE and bool(settings.OLLAMA_API_KEY)
        self._model_status = {}
        self.client = None

        if self.is_available:
            try:
                self.client = ollama.Client(
                    host="https://ollama.com",
                    headers={'Authorization': f'Bearer {settings.OLLAMA_API_KEY}'}
                )
                self.logger.info("✅ Ollama Cloud Service Initialized")
            except Exception as e:
                self.logger.error(f"Failed to init Ollama Cloud Client: {e}")
                self.is_available = False
    
    async def check_model_availability(self, model_type: str = "reasoning") -> bool:
        """Check if a model is available locally"""
        if not self.is_available:
            return False
        
        try:
            model_name = self.models.get(model_type, self.models["reasoning"])
            # Try to get model info
            models_list = self.client.list()
            available_models = [m.get('name', '') for m in models_list.get('models', [])]
            return any(model_name in m for m in available_models)
        except Exception as e:
            self.logger.error(f"Error checking model: {e}")
            return False
    
    async def invoke(
        self,
        prompt: str,
        model_type: str = "reasoning",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        reasoning_mode: bool = False,
        images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Invoke a local LLM with advanced options
        
        Args:
            prompt: User prompt
            model_type: "reasoning", "vision", "fast", "coding", "general"
            temperature: 0.0-1.0 (lower = deterministic, higher = creative)
            max_tokens: Maximum response length
            system_prompt: System instructions for the model
            reasoning_mode: Enable extended reasoning (DeepSeek-R1 only)
            images: List of base64 encoded images
            
        Returns:
            dict with response, model_used, tokens, etc.
        """
        
        if not self.is_available:
            self.logger.warning("Ollama Cloud not configured (missing key or lib)")
            return {"error": "Ollama Cloud Unavailable"}
        
        try:
            model_name = self.models.get(model_type, self.models["reasoning"])
            
            # Build message structure
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            user_msg = {
                "role": "user",
                "content": prompt
            }
            
            if images:
                user_msg["images"] = images
                
            messages.append(user_msg)
            
            # Model options
            options = {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
            
            # Extended reasoning for DeepSeek-R1
            if reasoning_mode and "deepseek-r1" in model_name:
                options["num_predict"] = max_tokens * 2
            
            self.logger.info(f"Invoking {model_name} with {len(prompt)} chars")
            
            # Call Ollama
            response = self.client.chat(
                model=model_name,
                messages=messages,
                options=options,
                stream=False
            )
            
            answer = response.get("message", {}).get("content", "")
            
            return {
                "response": answer,
                "model_used": model_name,
                "model_type": model_type,
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(answer.split()),
                "timestamp": datetime.now().isoformat(),
                "reasoning_used": reasoning_mode,
                "local": False,
                "cloud_provider": "ollama",
                "cost": 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Ollama Cloud invocation failed: {str(e)}")
            # Raise exception to let Router handle fallback to next provider (e.g. OpenAI)
            raise e
    
    async def stream_response(
        self,
        prompt: str,
        model_type: str = "reasoning",
        system_prompt: Optional[str] = None
    ):
        """Stream responses token-by-token for real-time display"""
        
        if not self.is_available:
            yield "Error: Ollama not available"
            return
        
        model_name = self.models.get(model_type, self.models["reasoning"])
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat(
                model=model_name,
                messages=messages,
                stream=True
            )
            
            for chunk in response:
                delta = chunk.get("message", {}).get("content", "")
                if delta:
                    yield delta
        except Exception as e:
            yield f"Error: {str(e)}"
    
    async def batch_invoke(
        self,
        prompts: List[str],
        model_type: str = "fast"
    ) -> List[Dict[str, Any]]:
        """Process multiple prompts in batch"""
        
        results = []
        for prompt in prompts:
            result = await self.invoke(prompt, model_type, max_tokens=500)
            results.append(result)
        
        return results
    
    async def compare_models(self, prompt: str) -> Dict[str, Any]:
        """Compare responses from multiple models for quality assurance"""
        
        results = {}
        
        for model_type in ["reasoning", "fast", "coding"]:
            try:
                result = await self.invoke(prompt, model_type, max_tokens=500)
                results[model_type] = {
                    "response": result.get("response"),
                    "model": result.get("model_used"),
                    "tokens": result.get("completion_tokens", 0)
                }
            except Exception as e:
                results[model_type] = {"error": str(e)}
        
        return results
    
    async def measure_performance(self, prompt: str) -> Dict[str, Any]:
        """Measure latency and quality of different models"""
        
        import time
        
        performance = {}
        
        for model_type in ["reasoning", "fast"]:
            start = time.time()
            
            try:
                result = await self.invoke(prompt, model_type, max_tokens=300)
                elapsed = time.time() - start
                
                tokens = result.get("completion_tokens", 0)
                performance[model_type] = {
                    "latency_sec": round(elapsed, 2),
                    "tokens_per_sec": round(tokens / elapsed, 1) if elapsed > 0 else 0,
                    "model": result.get("model_used"),
                    "success": True
                }
            except Exception as e:
                elapsed = time.time() - start
                performance[model_type] = {
                    "latency_sec": round(elapsed, 2),
                    "error": str(e),
                    "success": False
                }
        
        return performance
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status and available models"""
        return {
            "ollama_available": self.is_available,
            "models_configured": self.models,
            "fallback_models": self.fallback_models,
            "cloud_fallback_ready": True,
            "note": "Using Ollama Cloud API"
        }


# Singleton instance
ollama_service = OllamaCloudService()
