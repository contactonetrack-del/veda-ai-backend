"""
Vector Database Service - Phase 4
Local Qdrant vector store for RAG capabilities
Zero-cost with sentence-transformers embeddings
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Try to import Qdrant - will work after pip install
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qdrant_models
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None

# Try to import sentence-transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    SentenceTransformer = None


class VectorDatabaseService:
    """
    Local vector database for knowledge storage and RAG
    
    Uses:
    - Qdrant (local, free) for vector storage
    - sentence-transformers for embeddings (local, free)
    
    Features:
    - Store documents with embeddings
    - Semantic search
    - RAG-ready retrieval
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.embedding_model = None
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        self.default_collection = "veda_knowledge"
        
        # Initialize if available
        self._init_qdrant()
        self._init_embeddings()
    
    def _init_qdrant(self):
        """Initialize Qdrant client (in-memory or persistent)"""
        if not QDRANT_AVAILABLE:
            self.logger.warning("Qdrant not installed. Run: pip install qdrant-client")
            return
        
        try:
            # Use in-memory for simplicity (can switch to file-based)
            self.client = QdrantClient(":memory:")
            
            # Create default collection
            self.client.recreate_collection(
                collection_name=self.default_collection,
                vectors_config=qdrant_models.VectorParams(
                    size=self.embedding_dim,
                    distance=qdrant_models.Distance.COSINE
                )
            )
            
            self.logger.info("Qdrant initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Qdrant init failed: {e}")
            self.client = None
    
    def _init_embeddings(self):
        """Initialize embedding model"""
        if not EMBEDDINGS_AVAILABLE:
            self.logger.warning("sentence-transformers not installed. Run: pip install sentence-transformers")
            return
        
        try:
            # Use lightweight model for speed
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Embedding model loaded")
            
        except Exception as e:
            self.logger.error(f"Embedding model load failed: {e}")
            self.embedding_model = None
    
    def embed_text(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text"""
        if not self.embedding_model:
            return None
        
        try:
            embedding = self.embedding_model.encode(text).tolist()
            return embedding
        except Exception as e:
            self.logger.error(f"Embedding failed: {e}")
            return None
    
    def embed_batch(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Generate embeddings for multiple texts"""
        if not self.embedding_model:
            return None
        
        try:
            embeddings = self.embedding_model.encode(texts).tolist()
            return embeddings
        except Exception as e:
            self.logger.error(f"Batch embedding failed: {e}")
            return None
    
    async def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a document to the vector store
        
        Args:
            content: Text content to store
            metadata: Optional metadata (source, title, etc.)
            collection: Collection name (default: veda_knowledge)
        """
        if not self.client or not self.embedding_model:
            return {
                "success": False,
                "error": "Vector DB or embeddings not available"
            }
        
        collection = collection or self.default_collection
        
        try:
            # Generate embedding
            embedding = self.embed_text(content)
            if not embedding:
                return {"success": False, "error": "Embedding generation failed"}
            
            # Generate unique ID
            import uuid
            doc_id = str(uuid.uuid4())
            
            # Prepare payload
            payload = {
                "content": content,
                "added_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Insert into Qdrant
            self.client.upsert(
                collection_name=collection,
                points=[
                    qdrant_models.PointStruct(
                        id=doc_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            return {
                "success": True,
                "document_id": doc_id,
                "collection": collection
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def add_documents_batch(
        self,
        documents: List[Dict[str, Any]],
        collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add multiple documents at once
        
        Args:
            documents: List of {"content": str, "metadata": dict}
            collection: Collection name
        """
        if not self.client or not self.embedding_model:
            return {"success": False, "error": "Vector DB not available"}
        
        collection = collection or self.default_collection
        
        try:
            contents = [doc["content"] for doc in documents]
            embeddings = self.embed_batch(contents)
            
            if not embeddings:
                return {"success": False, "error": "Batch embedding failed"}
            
            import uuid
            points = []
            
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                doc_id = str(uuid.uuid4())
                payload = {
                    "content": doc["content"],
                    "added_at": datetime.now().isoformat(),
                    **(doc.get("metadata") or {})
                }
                points.append(
                    qdrant_models.PointStruct(
                        id=doc_id,
                        vector=embedding,
                        payload=payload
                    )
                )
            
            self.client.upsert(collection_name=collection, points=points)
            
            return {
                "success": True,
                "documents_added": len(points),
                "collection": collection
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        collection: Optional[str] = None,
        score_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Semantic search for relevant documents
        
        Args:
            query: Search query
            limit: Max results to return
            collection: Collection to search
            score_threshold: Minimum similarity score
        """
        if not self.client or not self.embedding_model:
            return {"success": False, "results": [], "error": "Vector DB not available"}
        
        collection = collection or self.default_collection
        
        try:
            # Generate query embedding
            query_embedding = self.embed_text(query)
            if not query_embedding:
                return {"success": False, "results": [], "error": "Query embedding failed"}
            
            # Search using query method (new API in qdrant-client v1.16+)
            results = self.client.query_points(
                collection_name=collection,
                query=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted = []
            for result in results.points:
                formatted.append({
                    "id": result.id,
                    "score": result.score,
                    "content": result.payload.get("content", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "content"}
                })
            
            return {
                "success": True,
                "results": formatted,
                "query": query,
                "collection": collection
            }
            
        except Exception as e:
            return {"success": False, "results": [], "error": str(e)}
    
    async def get_context_for_rag(
        self,
        query: str,
        limit: int = 3,
        collection: Optional[str] = None
    ) -> str:
        """
        Get relevant context for RAG (formatted for LLM)
        
        Returns concatenated context from top results
        """
        search_result = await self.search(query, limit=limit, collection=collection)
        
        if not search_result.get("success") or not search_result.get("results"):
            return ""
        
        # Format context for LLM
        contexts = []
        for i, result in enumerate(search_result["results"], 1):
            content = result.get("content", "")
            source = result.get("metadata", {}).get("source", "Unknown")
            contexts.append(f"[Source {i}: {source}]\n{content}")
        
        return "\n\n---\n\n".join(contexts)
    
    def get_status(self) -> Dict[str, Any]:
        """Get vector database status"""
        
        collection_info = None
        if self.client:
            try:
                info = self.client.get_collection(self.default_collection)
                collection_info = {
                    "name": self.default_collection,
                    "vectors_count": info.vectors_count,
                    "points_count": info.points_count
                }
            except:
                pass
        
        return {
            "qdrant_available": QDRANT_AVAILABLE,
            "qdrant_connected": self.client is not None,
            "embeddings_available": EMBEDDINGS_AVAILABLE,
            "embedding_model": "all-MiniLM-L6-v2" if self.embedding_model else None,
            "embedding_dimension": self.embedding_dim,
            "default_collection": self.default_collection,
            "collection_info": collection_info,
            "cost": "$0 (all local)"
        }


# Singleton instance
vector_db = VectorDatabaseService()
