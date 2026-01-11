"""
Advanced Reasoning API Routes - Phase 2
Endpoints for advanced reasoning capabilities
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.reasoning_engine import reasoning_engine

router = APIRouter(tags=["Advanced Reasoning"])


class ReasoningRequest(BaseModel):
    """Request for advanced reasoning"""
    query: str
    method: str = "auto"  # auto, chain_of_thought, tree_of_thought, self_consistency, decomposed
    context: Optional[str] = None
    num_attempts: int = 3  # For self_consistency
    num_paths: int = 3  # For tree_of_thought


class ReasoningResponse(BaseModel):
    """Response from reasoning engine"""
    response: Optional[str]
    method: str
    model: Optional[str]
    complexity: Optional[str]
    local: bool = True
    cost: float = 0.0
    error: Optional[str] = None


@router.post("/query", response_model=None)
async def advanced_reasoning(request: ReasoningRequest) -> Dict[str, Any]:
    """
    Execute advanced reasoning on a query
    
    Methods:
    - **auto**: Automatically selects best method based on query
    - **chain_of_thought**: Step-by-step reasoning (2-3x accuracy)
    - **tree_of_thought**: Explore multiple paths (4-5x on complex)
    - **self_consistency**: Vote on best answer (40% error reduction)
    - **decomposed**: Break into sub-problems
    """
    
    try:
        if request.method == "auto":
            result = await reasoning_engine.auto_reason(
                query=request.query,
                context=request.context
            )
        elif request.method == "chain_of_thought":
            result = await reasoning_engine.chain_of_thought(
                query=request.query,
                context=request.context
            )
        elif request.method == "tree_of_thought":
            result = await reasoning_engine.tree_of_thought(
                query=request.query,
                num_paths=request.num_paths
            )
        elif request.method == "self_consistency":
            result = await reasoning_engine.self_consistency(
                query=request.query,
                num_attempts=request.num_attempts
            )
        elif request.method == "decomposed":
            result = await reasoning_engine.decomposed_reasoning(
                query=request.query
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown method: {request.method}. Use: auto, chain_of_thought, tree_of_thought, self_consistency, decomposed"
            )
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "method": request.method,
            "response": None
        }


@router.post("/chain-of-thought")
async def chain_of_thought(query: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Chain-of-Thought reasoning
    
    Best for: Math, logic, analysis questions
    Improvement: 2-3x accuracy
    """
    return await reasoning_engine.chain_of_thought(query, context)


@router.post("/tree-of-thought")
async def tree_of_thought(query: str, num_paths: int = 3) -> Dict[str, Any]:
    """
    Tree-of-Thought reasoning
    
    Best for: Complex decisions, planning, creative problems
    Improvement: 4-5x on complex problems
    """
    return await reasoning_engine.tree_of_thought(query, num_paths)


@router.post("/self-consistency")
async def self_consistency(query: str, num_attempts: int = 3) -> Dict[str, Any]:
    """
    Self-Consistency voting
    
    Best for: Fact-based questions, calculations, verification
    Improvement: 40% error reduction
    """
    return await reasoning_engine.self_consistency(query, num_attempts)


@router.post("/decomposed")
async def decomposed_reasoning(query: str) -> Dict[str, Any]:
    """
    Decomposed reasoning
    
    Best for: Multi-step problems, planning, research
    """
    return await reasoning_engine.decomposed_reasoning(query)


@router.get("/methods")
async def get_methods() -> Dict[str, Any]:
    """
    List available reasoning methods
    """
    return {
        "methods": reasoning_engine.get_methods(),
        "recommended": {
            "math_problems": "self_consistency",
            "decisions": "tree_of_thought",
            "planning": "decomposed",
            "general": "chain_of_thought",
            "unknown": "auto"
        },
        "cost": "$0 (all methods use local LLM)"
    }
