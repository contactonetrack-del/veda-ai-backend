"""
Vector Memory Service using ChromaDB
Stores and retrieves conversation context for personalized AI responses
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict
import uuid
from datetime import datetime

class VectorMemory:
    def __init__(self):
        # Persistent storage in ./chroma_db directory
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Create or get collection for conversations
        self.collection = self.client.get_or_create_collection(
            name="veda_conversations",
            metadata={"description": "User conversation history for context retrieval"}
        )
    
    async def add_message(
        self, 
        user_id: str, 
        message: str, 
        role: str,
        embedding: List[float],
        metadata: Dict = None
    ) -> str:
        """
        Store a message with its embedding in ChromaDB
        Returns the document ID
        """
        doc_id = str(uuid.uuid4())
        
        # Prepare metadata - filter out None values (ChromaDB requirement)
        meta = {
            "user_id": user_id,
            "role": role,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Merge additional metadata, filtering out None values
        if metadata:
            for key, value in metadata.items():
                if value is not None:
                    meta[key] = str(value) if not isinstance(value, (str, int, float, bool)) else value
        
        # Add to collection
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[message],
            metadatas=[meta]
        )
        
        return doc_id
    
    async def search_context(
        self, 
        user_id: str, 
        query_embedding: List[float], 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant past messages for a user
        Returns list of {message, role, timestamp} dicts
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"user_id": user_id}  # Filter by user for privacy
        )
        
        # Format results
        context = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i, doc in enumerate(results['documents'][0]):
                context.append({
                    "message": doc,
                    "role": results['metadatas'][0][i]['role'],
                    "timestamp": results['metadatas'][0][i]['timestamp']
                })
        
        return context

# Singleton instance
vector_memory = VectorMemory()
