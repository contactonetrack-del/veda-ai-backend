from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class MessageCreate(BaseModel):
    content: str
    model: Optional[str] = "gemini-2.5-flash"

class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

class ChatCreate(BaseModel):
    title: Optional[str] = "New Chat"

class ChatResponse(BaseModel):
    id: UUID
    title: Optional[str]
    created_at: datetime
    # messages: List[MessageResponse] = [] # Optional, loaded separately usually
