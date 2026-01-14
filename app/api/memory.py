from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.services.memory import vector_memory

router = APIRouter()

class MemoryItem(BaseModel):
    id: str
    text: str
    metadata: Dict
    created_at: Optional[str]

@router.get("/", response_model=List[MemoryItem])
async def get_memories(user_id: str, limit: int = 50):
    """Get recent memories for a user"""
    memories = await vector_memory.get_memories(user_id, limit)
    return memories

@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, user_id: str):
    """Delete a specific memory"""
    success = await vector_memory.delete_memory(user_id, memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found or access denied")
    return {"status": "deleted", "id": memory_id}

@router.delete("/")
async def clear_history(user_id: str):
    """Clear all memory for a user"""
    success = await vector_memory.clear_history(user_id)
    return {"status": "cleared" if success else "failed"}
