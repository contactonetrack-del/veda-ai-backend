"""
Domain Expert Router - Phase 3
Intelligent routing to 12 specialized domain experts
Uses local LLM for intent detection → zero cost
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.local_llm import local_llm_service
from app.services.reasoning_engine import reasoning_engine
from app.agents.domain_experts import DOMAIN_EXPERTS, get_expert_response

router = APIRouter(tags=["Domain Experts"])


class ExpertQueryRequest(BaseModel):
    """Request for domain expert query"""
    query: str
    expert: Optional[str] = None  # Auto-detect if not specified
    use_reasoning: bool = False  # Use advanced reasoning
    reasoning_method: str = "auto"  # chain_of_thought, tree_of_thought, etc.
    context: Optional[str] = None


class ExpertQueryResponse(BaseModel):
    """Response from domain expert"""
    response: Optional[str]
    expert_used: str
    intent_detected: str
    reasoning_method: Optional[str] = None
    local: bool = True
    cost: float = 0.0


# Intent detection keywords for routing
INTENT_KEYWORDS = {
    "career": ["resume", "interview", "job", "career", "salary", "hire", "linkedin", "cv", "promotion"],
    "mental_health": ["stress", "anxiety", "meditation", "mindful", "mental", "therapy", "depress", "calm", "relax"],
    "study": ["learn", "study", "exam", "homework", "tutor", "explain", "understand", "concept", "student"],
    "legal": ["legal", "law", "contract", "rights", "court", "sue", "lawyer", "agreement"],
    "finance": ["budget", "tax", "invest", "saving", "money", "income", "expense", "loan", "emi", "sip"],
    "content": ["write", "blog", "caption", "headline", "copy", "article", "content", "seo", "marketing"],
    "code": ["code", "debug", "error", "bug", "programming", "python", "javascript", "function", "api"],
    "travel": ["travel", "trip", "vacation", "itinerary", "hotel", "flight", "destination", "tour"],
    "parenting": ["child", "parent", "baby", "kid", "toddler", "discipline", "school", "homework"],
    "relationship": ["relationship", "partner", "marriage", "dating", "communication", "conflict", "love"],
    "health": ["health", "diet", "nutrition", "weight", "calories", "exercise", "medical", "symptom", "pain"],
    "fitness": ["workout", "gym", "muscle", "training", "cardio", "strength", "routine", "exercise"]
}


async def detect_intent(query: str) -> str:
    """
    Detect user intent from query using keyword matching
    Falls back to LLM-based detection for ambiguous cases
    """
    query_lower = query.lower()
    
    # Score each intent based on keyword matches
    scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[intent] = score
    
    # Return highest scoring intent
    if scores:
        best_intent = max(scores, key=scores.get)
        return best_intent
    
    # Fallback: Use LLM for intent detection
    try:
        intent_prompt = f"""Classify this query into ONE category:

Query: "{query}"

Categories:
- career (job, interview, resume)
- mental_health (stress, anxiety, mindfulness)
- study (learning, tutoring, exams)
- legal (contracts, rights, law)
- finance (money, tax, investments)
- content (writing, marketing, social media)
- code (programming, debugging)
- travel (trips, itineraries)
- parenting (childcare, education)
- relationship (dating, communication)
- health (medical, nutrition)
- fitness (workout, exercise)
- general (none of the above)

Reply with ONLY the category name, nothing else."""

        result = await local_llm_service.invoke(
            prompt=intent_prompt,
            model_type="fast",
            max_tokens=20,
            temperature=0.1
        )
        
        detected = result.get("response", "general").strip().lower()
        # Validate it's a known intent
        if detected in DOMAIN_EXPERTS or detected in INTENT_KEYWORDS:
            return detected
        return "general"
        
    except Exception:
        return "general"


@router.post("/query")
async def query_expert(request: ExpertQueryRequest) -> Dict[str, Any]:
    """
    Query a domain expert
    
    Auto-detects intent if expert not specified.
    Optionally applies advanced reasoning.
    """
    
    # Detect intent if expert not specified
    if request.expert:
        intent = request.expert
    else:
        intent = await detect_intent(request.query)
    
    # Apply advanced reasoning if requested
    if request.use_reasoning:
        if request.reasoning_method == "auto":
            result = await reasoning_engine.auto_reason(request.query, request.context)
        elif request.reasoning_method == "chain_of_thought":
            result = await reasoning_engine.chain_of_thought(request.query, request.context)
        elif request.reasoning_method == "tree_of_thought":
            result = await reasoning_engine.tree_of_thought(request.query)
        elif request.reasoning_method == "self_consistency":
            result = await reasoning_engine.self_consistency(request.query)
        else:
            result = await reasoning_engine.decomposed_reasoning(request.query)
        
        return {
            "response": result.get("response"),
            "expert_used": "Advanced Reasoning",
            "intent_detected": intent,
            "reasoning_method": request.reasoning_method,
            "local": True,
            "cost": 0.0
        }
    
    # Get response from domain expert
    result = await get_expert_response(intent, request.query, {"context": request.context})
    
    return {
        "response": result.get("response"),
        "expert_used": result.get("agent", "General"),
        "intent_detected": intent,
        "reasoning_method": None,
        "local": True,
        "cost": 0.0
    }


@router.get("/list")
async def list_experts() -> Dict[str, Any]:
    """
    List all available domain experts
    """
    
    experts = []
    for key, agent in DOMAIN_EXPERTS.items():
        experts.append({
            "id": key,
            "name": agent.name,
            "description": agent.description
        })
    
    return {
        "experts": experts,
        "total": len(experts),
        "cost": "$0/month (all local)"
    }


@router.post("/detect-intent")
async def detect_query_intent(query: str) -> Dict[str, Any]:
    """
    Detect the intent/domain of a query without executing
    """
    
    intent = await detect_intent(query)
    
    # Get the expert name if available
    expert_name = "General"
    if intent in DOMAIN_EXPERTS:
        expert_name = DOMAIN_EXPERTS[intent].name
    
    return {
        "query": query,
        "intent": intent,
        "expert_name": expert_name,
        "keywords_matched": [kw for kw in INTENT_KEYWORDS.get(intent, []) if kw in query.lower()]
    }


@router.get("/intents")
async def list_intents() -> Dict[str, Any]:
    """
    List all detectable intents and their keywords
    """
    
    return {
        "intents": {
            intent: {
                "keywords": keywords,
                "expert": DOMAIN_EXPERTS.get(intent, {}).name if intent in DOMAIN_EXPERTS else "General"
            }
            for intent, keywords in INTENT_KEYWORDS.items()
        }
    }
