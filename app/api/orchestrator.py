"""
Orchestrator API Routes
Multi-agent query processing with citations
Phase 1: Perplexity-class Intelligence
Phase 2: Fact-checking verification
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime
from app.orchestrator import orchestrator

router = APIRouter()


class QueryRequest(BaseModel):
    """Request model for orchestrator queries"""
    message: str
    context: Optional[Dict] = {}
    user_id: Optional[str] = "guest"
    verify_facts: Optional[bool] = True  # Phase 2: Enable fact-checking


class SourceModel(BaseModel):
    """Source/citation model"""
    title: str
    url: str
    favicon: Optional[str] = ""
    source_type: Optional[str] = "web"


class QueryResponse(BaseModel):
    """Response model with citations"""
    response: str
    intent: str
    agent_used: str
    sources: List[Dict] = []
    reviewed: bool
    context_used: bool
    verified: bool = False  # Phase 2: Fact-check verification status
    confidence: float = 0.0  # Phase 2: Confidence score (0-1)
    timestamp: str


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query through the multi-agent orchestrator.
    
    This endpoint:
    1. Routes the query to the appropriate specialist agent
    2. Returns the response with citations (if search was used)
    3. Includes metadata about which agent handled the query
    
    Examples:
    - "Calculate my BMI" → ToolAgent
    - "What's the latest research on fasting?" → SearchAgent (with citations)
    - "Best exercises for weight loss" → WellnessAgent
    """
    try:
        result = await orchestrator.process_message(
            user_message=request.message,
            user_id=request.user_id or "guest",
            chat_id=None,
            verify_facts=request.verify_facts
        )
        
        return QueryResponse(
            response=result.get("response", ""),
            intent=result.get("intent", "general"),
            agent_used=result.get("agent_used", "GeneralAgent"),
            sources=result.get("sources", []),
            reviewed=result.get("reviewed", True),
            context_used=result.get("context_used", False),
            verified=result.get("verified", False),
            confidence=result.get("confidence", 0.0),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        print(f"[Orchestrator API] Error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process query: {str(e)}"
        )


@router.get("/status")
async def get_status():
    """
    Get orchestrator status and available agents.
    """
    from app.services.web_search import web_search
    
    return {
        "status": "operational",
        "agents": list(orchestrator.agents.keys()),
        "web_search_available": web_search.is_available,
        "search_usage": web_search.get_usage_stats(),
        "timestamp": datetime.now().isoformat()
    }
