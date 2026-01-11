"""
Local LLM Service - Phase 1
Manages Ollama models for local AI inference
Zero-cost alternative to cloud APIs (Groq, OpenAI)
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

# Check if ollama is available
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("Ollama not installed. Run: pip install ollama")

from app.services.cloud_ai import cloud_ai_service


class LocalLLMService:
    """
    Advanced local LLM service with model management
    
    Models (all FREE via Ollama):
    - reasoning: DeepSeek-R1 7B (math, logic, complex tasks)
    - vision: Llama 3.2 Vision (image analysis)
    - fast: Phi-3.5 Mini (quick responses)
    - coding: Qwen2.5 (code tasks)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Model configuration (can be updated based on installed models)
        self.models = {
            "reasoning": "deepseek-r1:7b",           # Best for complex tasks
            "vision": "llama3.2-vision:11b",         # Image analysis
            "fast": "phi3.5:latest",                 # Quick responses
            "coding": "qwen2.5:7b",                  # Code tasks
            "general": "llama3.2:latest",            # General purpose
        }
        
        # Fallback models if primary not available
        self.fallback_models = {
            "reasoning": "qwen2.5:7b",
            "vision": "llama3.2:latest",
            "fast": "phi:latest",
            "coding": "deepseek-r1:7b",
        }
        
        self.is_available = OLLAMA_AVAILABLE
        self._model_status = {}
    
    async def check_model_availability(self, model_type: str = "reasoning") -> bool:
        """Check if a model is available locally"""
        if not self.is_available:
            return False
        
        try:
            model_name = self.models.get(model_type, self.models["reasoning"])
            # Try to get model info
            models_list = ollama.list()
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
        reasoning_mode: bool = False
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
            
        Returns:
            dict with response, model_used, tokens, etc.
        """
        
        if not self.is_available:
            self.logger.warning("Ollama not available, falling back to Cloud AI")
            return await cloud_ai_service.invoke(
                prompt=prompt,
                system_prompt=system_prompt,
                model_preference="fast" if model_type == "fast" else "utility",
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        try:
            model_name = self.models.get(model_type, self.models["reasoning"])
            
            # Build message structure
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
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
            response = ollama.chat(
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
                "local": True,
                "cost": 0.0  # Zero cost!
            }
            
        except Exception as e:
            self.logger.error(f"Local LLM invocation failed: {str(e)}")
            self.logger.info("Falling back to Cloud AI...")
            return await cloud_ai_service.invoke(
                prompt=prompt,
                system_prompt=system_prompt,
                model_preference="fast" if model_type == "fast" else "utility",
                temperature=temperature,
                max_tokens=max_tokens
            )
    
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
            response = ollama.chat(
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
            "cloud_fallback": cloud_ai_service.get_status(),
            "note": "Local AI uses Ollama. Cloud Fallback active for 24/7 availability."
        }


# Singleton instance
local_llm_service = LocalLLMService()
