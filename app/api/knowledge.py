"""
Knowledge Base API Routes - Phase 4
Endpoints for RAG and knowledge management
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.rag_service import rag_service
from app.services.vector_db import vector_db

router = APIRouter(tags=["Knowledge Base"])


class KnowledgeAddRequest(BaseModel):
    """Request to add knowledge"""
    content: str
    source: str = "manual"
    title: Optional[str] = None
    category: Optional[str] = None
    collection: Optional[str] = None


class KnowledgeBatchRequest(BaseModel):
    """Request to add multiple knowledge items"""
    items: List[Dict[str, str]]  # [{"content": str, "source": str, ...}]
    collection: Optional[str] = None


class RAGQueryRequest(BaseModel):
    """Request for RAG query"""
    query: str
    collection: Optional[str] = None
    num_contexts: int = 3
    model_type: str = "reasoning"
    include_sources: bool = True


class SearchRequest(BaseModel):
    """Request for knowledge search"""
    query: str
    limit: int = 5
    collection: Optional[str] = None


@router.post("/add")
async def add_knowledge(request: KnowledgeAddRequest) -> Dict[str, Any]:
    """
    Add knowledge to the vector database
    
    This knowledge will be used for RAG-enhanced responses.
    """
    
    return await rag_service.add_knowledge(
        content=request.content,
        source=request.source,
        title=request.title,
        category=request.category,
        collection=request.collection
    )


@router.post("/add-batch")
async def add_knowledge_batch(request: KnowledgeBatchRequest) -> Dict[str, Any]:
    """
    Add multiple knowledge items at once
    """
    
    return await rag_service.add_knowledge_batch(
        items=request.items,
        collection=request.collection
    )


@router.post("/query")
async def rag_query(request: RAGQueryRequest) -> Dict[str, Any]:
    """
    RAG Query: Search knowledge base + generate enhanced response
    
    This is the main RAG endpoint. It:
    1. Searches your knowledge base for relevant context
    2. Uses that context to generate an accurate response
    3. Includes source citations
    """
    
    return await rag_service.query_with_context(
        query=request.query,
        collection=request.collection,
        num_contexts=request.num_contexts,
        model_type=request.model_type,
        include_sources=request.include_sources
    )


@router.post("/search")
async def search_knowledge(request: SearchRequest) -> Dict[str, Any]:
    """
    Search the knowledge base (without LLM generation)
    
    Returns matching documents with similarity scores.
    """
    
    return await rag_service.search_knowledge(
        query=request.query,
        limit=request.limit,
        collection=request.collection
    )


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Get RAG and knowledge base status
    """
    
    return rag_service.get_status()


@router.get("/vector-db/status")
async def get_vector_db_status() -> Dict[str, Any]:
    """
    Get vector database status
    """
    
    return vector_db.get_status()
