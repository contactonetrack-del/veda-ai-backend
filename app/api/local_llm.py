"""
Ollama Cloud API Routes - Phase 2
API endpoints for cloud-native inference via Ollama Cloud
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.ollama_service import ollama_service

router = APIRouter(tags=["Ollama Cloud"])


class OllamaQueryRequest(BaseModel):
    """Request model for Ollama Cloud queries"""
    prompt: str
    model_type: str = "reasoning"  # reasoning, vision, fast, coding, general
    temperature: float = 0.7
    max_tokens: int = 2000
    system_prompt: Optional[str] = None
    reasoning_mode: bool = False


class OllamaQueryResponse(BaseModel):
    """Response model for Ollama Cloud queries"""
    response: Optional[str]
    model_used: Optional[str]
    model_type: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    timestamp: str = ""
    reasoning_used: bool = False
    local: bool = False
    cloud_provider: str = "ollama"
    cost: float = 0.0
    error: Optional[str] = None


@router.post("/query", response_model=OllamaQueryResponse)
async def query_ollama_cloud(request: OllamaQueryRequest) -> Dict[str, Any]:
    """
    Query Ollama Cloud directly (Next-Gen Models)
    
    Cloud Native Inference using Tier-1 Models:
    - **reasoning**: DeepSeek-V3.1 671B (State-of-the-art medical logic)
    - **vision**: Gemini-3 Flash Preview (Next-gen visual analysis)
    - **fast**: GPT-OSS 20B (Instant latency)
    - **coding**: Qwen3-Coder 480B (Complex logic giant)
    """
    
    result = await ollama_service.invoke(
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
    Compare responses from multiple cloud models
    """
    
    return await ollama_service.compare_models(prompt)


@router.post("/benchmark")
async def benchmark_models(prompt: str) -> Dict[str, Any]:
    """
    Benchmark model performance (latency, tokens/sec)
    """
    
    return await ollama_service.measure_performance(prompt)


@router.get("/status")
async def check_status() -> Dict[str, Any]:
    """
    Check Ollama Cloud Service status and available models
    """
    
    status = ollama_service.get_status()
    
    # Check if specific model is available (in cloud)
    # Note: Cloud availability is usually guaranteed if key is valid
    reasoning_available = ollama_service.is_available
    
    status["models_status"] = {
        "reasoning": "available" if reasoning_available else "unavailable",
        "cloud_mode": True
    }
    
    return status


@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """
    List all configured cloud models and their purposes
    """
    
    return {
        "models": [
            {
                "type": "reasoning",
                "name": "deepseek-v3.1:671b",
                "purpose": "State-of-the-art medical reasoning & diet logic",
                "tier": "Tier 1",
                "availability": "Cloud"
            },
            {
                "type": "vision",
                "name": "gemini-3-flash-preview",
                "purpose": "Next-gen meal/food image analysis",
                "tier": "Tier 1",
                "availability": "Cloud"
            },
            {
                "type": "fast",
                "name": "gpt-oss:20b",
                "purpose": "Low-latency UI interactions",
                "tier": "Fast",
                "availability": "Cloud"
            },
            {
                "type": "coding",
                "name": "qwen3-coder:480b",
                "purpose": "Backend logic and code generation",
                "tier": "Tier 1",
                "availability": "Cloud"
            }
        ],
        "infrastructure": "Ollama Cloud Native",
        "status": "Production Ready"
    }
