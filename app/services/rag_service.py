"""
RAG (Retrieval-Augmented Generation) Service - Phase 4
Enhances LLM responses with knowledge base context
Zero-cost implementation using local models
"""
import logging
from typing import Dict, Any, Optional, List
from app.services.vector_db import vector_db
from app.services.local_llm import local_llm_service


class RAGService:
    """
    Retrieval-Augmented Generation for enhanced responses
    
    Flow:
    1. Query → Vector search for relevant context
    2. Context + Query → LLM generates enhanced response
    3. Response includes citations from knowledge base
    
    Benefits:
    - More accurate, factual responses
    - Grounded in your custom knowledge
    - Zero hallucination for known facts
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.vector_db = vector_db
        self.llm = local_llm_service
    
    async def query_with_context(
        self,
        query: str,
        collection: Optional[str] = None,
        num_contexts: int = 3,
        model_type: str = "reasoning",
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        RAG query: Search knowledge base + generate response
        
        Args:
            query: User question
            collection: Knowledge base collection to search
            num_contexts: Number of context chunks to retrieve
            model_type: LLM model to use
            include_sources: Include source citations
        """
        
        # Step 1: Retrieve relevant context
        context = await self.vector_db.get_context_for_rag(
            query=query,
            limit=num_contexts,
            collection=collection
        )
        
        # Step 2: Build RAG prompt
        if context:
            rag_prompt = f"""Answer the user's question using the provided context. 
If the context doesn't contain relevant information, say so and provide your best answer.

CONTEXT FROM KNOWLEDGE BASE:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
1. Use the context to provide an accurate, factual answer
2. If citing the context, mention the source number
3. If the context is insufficient, acknowledge this
4. Be concise but comprehensive

ANSWER:"""
        else:
            # No context found - use standard query
            rag_prompt = f"""Answer this question to the best of your ability:

{query}

Note: No relevant context was found in the knowledge base, so this answer is based on general knowledge."""
        
        # Step 3: Generate response
        result = await self.llm.invoke(
            prompt=rag_prompt,
            model_type=model_type,
            max_tokens=2000,
            temperature=0.3  # Lower for factual accuracy
        )
        
        # Step 4: Search results for citations
        sources = []
        if include_sources and context:
            search_result = await self.vector_db.search(
                query=query,
                limit=num_contexts,
                collection=collection
            )
            if search_result.get("success"):
                sources = [
                    {
                        "content_preview": r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"],
                        "score": round(r["score"], 3),
                        "metadata": r.get("metadata", {})
                    }
                    for r in search_result.get("results", [])
                ]
        
        return {
            "response": result.get("response"),
            "context_used": bool(context),
            "sources": sources,
            "model_used": result.get("model_used"),
            "query": query,
            "local": True,
            "cost": 0.0
        }
    
    async def add_knowledge(
        self,
        content: str,
        source: str = "manual",
        title: Optional[str] = None,
        category: Optional[str] = None,
        collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add knowledge to the RAG knowledge base
        
        Args:
            content: Text content to add
            source: Where this knowledge came from
            title: Optional title/label
            category: Optional category for filtering
            collection: Target collection
        """
        
        metadata = {
            "source": source,
            "title": title or "Untitled",
            "category": category or "general"
        }
        
        result = await self.vector_db.add_document(
            content=content,
            metadata=metadata,
            collection=collection
        )
        
        return result
    
    async def add_knowledge_batch(
        self,
        items: List[Dict[str, Any]],
        collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add multiple knowledge items at once
        
        Args:
            items: List of {"content": str, "source": str, "title": str, "category": str}
        """
        
        documents = []
        for item in items:
            documents.append({
                "content": item.get("content", ""),
                "metadata": {
                    "source": item.get("source", "manual"),
                    "title": item.get("title", "Untitled"),
                    "category": item.get("category", "general")
                }
            })
        
        result = await self.vector_db.add_documents_batch(
            documents=documents,
            collection=collection
        )
        
        return result
    
    async def search_knowledge(
        self,
        query: str,
        limit: int = 5,
        collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search the knowledge base
        """
        
        return await self.vector_db.search(
            query=query,
            limit=limit,
            collection=collection
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get RAG service status"""
        
        db_status = self.vector_db.get_status()
        llm_status = self.llm.get_status()
        
        return {
            "rag_available": db_status.get("qdrant_available") and llm_status.get("ollama_available"),
            "vector_db": db_status,
            "llm": llm_status,
            "features": [
                "Semantic search",
                "Context retrieval",
                "Enhanced LLM responses",
                "Source citations",
                "Knowledge management"
            ],
            "cost": "$0 (all local)"
        }


# Singleton instance
rag_service = RAGService()
