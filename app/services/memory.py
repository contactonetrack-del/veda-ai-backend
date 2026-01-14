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
    
    async def get_memories(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get recent memories for a user
        """
        try:
            results = self.collection.get(
                where={"user_id": user_id},
                limit=limit,
                include=["documents", "metadatas", "embeddings"]
            )
            
            memories = []
            if results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    memories.append({
                        "id": doc_id,
                        "text": results['documents'][i],
                        "metadata": results['metadatas'][i],
                        "created_at": results['metadatas'][i].get('timestamp')
                    })
            return sorted(memories, key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            print(f"Error fetching memories: {e}")
            return []

    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """
        Delete a specific memory
        """
        try:
            # Verify ownership
            existing = self.collection.get(ids=[memory_id], where={"user_id": user_id})
            if not existing['ids']:
                return False
                
            self.collection.delete(ids=[memory_id])
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False

    async def clear_history(self, user_id: str) -> bool:
        """Clear all memories for a user"""
        try:
            self.collection.delete(where={"user_id": user_id})
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False

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
        try:
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
        except Exception as e:
            print(f"Search Vector Context Error: {e}")
            return []

# Singleton instance
vector_memory = VectorMemory()
