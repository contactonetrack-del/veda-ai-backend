"""
Local LLM API Routes - Phase 1
API endpoints for local LLM inference via Ollama
Zero-cost alternative to cloud APIs
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.local_llm import local_llm_service

router = APIRouter(tags=["Local LLM"])


class LocalQueryRequest(BaseModel):
    """Request model for local LLM queries"""
    prompt: str
    model_type: str = "reasoning"  # reasoning, vision, fast, coding, general
    temperature: float = 0.7
    max_tokens: int = 2000
    system_prompt: Optional[str] = None
    reasoning_mode: bool = False


class LocalQueryResponse(BaseModel):
    """Response model for local LLM queries"""
    response: Optional[str]
    model_used: Optional[str]
    model_type: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    timestamp: str = ""
    reasoning_used: bool = False
    local: bool = True
    cost: float = 0.0
    error: Optional[str] = None


@router.post("/query", response_model=LocalQueryResponse)
async def query_local_llm(request: LocalQueryRequest) -> Dict[str, Any]:
    """
    Query local LLM directly (bypass cloud APIs)
    
    Zero-cost inference using Ollama models:
    - **reasoning**: DeepSeek-R1 7B (math, logic, complex tasks)
    - **vision**: Llama 3.2 Vision (image analysis)
    - **fast**: Phi-3.5 Mini (quick responses)
    - **coding**: Qwen2.5 (code tasks)
    """
    
    result = await local_llm_service.invoke(
        prompt=request.prompt,
        model_type=request.model_type,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        system_prompt=request.system_prompt,
        reasoning_mode=request.reasoning_mode
    )
    
    return result


@router.post("/compare")
async def compare_models(prompt: str) -> Dict[str, Any]:
    """
    Compare responses from multiple local models
    
    Useful for quality assurance and model selection
    """
    
    return await local_llm_service.compare_models(prompt)


@router.post("/benchmark")
async def benchmark_models(prompt: str) -> Dict[str, Any]:
    """
    Benchmark model performance (latency, tokens/sec)
    
    Use to optimize model selection for different use cases
    """
    
    return await local_llm_service.measure_performance(prompt)


@router.get("/status")
async def check_status() -> Dict[str, Any]:
    """
    Check local LLM service status and available models
    
    Returns:
    - ollama_available: whether Ollama is installed
    - models_configured: model name mappings
    - instructions for setup
    """
    
    status = local_llm_service.get_status()
    
    # Check if specific model is available
    reasoning_available = await local_llm_service.check_model_availability("reasoning")
    fast_available = await local_llm_service.check_model_availability("fast")
    
    status["models_status"] = {
        "reasoning": "available" if reasoning_available else "not_installed",
        "fast": "available" if fast_available else "not_installed"
    }
    
    return status


@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """
    List all configured models and their purposes
    """
    
    return {
        "models": [
            {
                "type": "reasoning",
                "name": "deepseek-r1:7b",
                "purpose": "Complex problems, math, logic, step-by-step thinking",
                "vram": "8GB",
                "speed": "15-20 tokens/sec"
            },
            {
                "type": "vision",
                "name": "llama3.2-vision:11b",
                "purpose": "Image analysis, visual understanding",
                "vram": "6GB",
                "speed": "20-30 tokens/sec"
            },
            {
                "type": "fast",
                "name": "phi3.5:latest",
                "purpose": "Quick responses, summarization",
                "vram": "3GB",
                "speed": "40+ tokens/sec"
            },
            {
                "type": "coding",
                "name": "qwen2.5:7b",
                "purpose": "Code review, debugging, programming",
                "vram": "7GB",
                "speed": "18 tokens/sec"
            }
        ],
        "total_cost": "$0/month",
        "setup": "Run: ollama pull <model_name>"
    }
