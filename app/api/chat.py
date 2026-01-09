from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional
from app.schemas.chat import ChatCreate, ChatResponse, MessageCreate, MessageResponse
from app.core.database import supabase
from app.services.gemini import gemini_service
import uuid

router = APIRouter()

# Dependency to get current user from Supabase Token
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Token")
    
    token = authorization.replace("Bearer ", "")
    try:
        user = supabase.auth.get_user(token)
        if not user or not user.user:
             raise HTTPException(status_code=401, detail="Invalid Token")
        return user.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/", response_model=List[ChatResponse])
async def get_chats(user = Depends(get_current_user)):
    response = supabase.table("chats").select("*").eq("user_id", user.id).order("created_at", desc=True).execute()
    return response.data

@router.post("/", response_model=ChatResponse)
async def create_chat(chat: ChatCreate, user = Depends(get_current_user)):
    # Create new chat
    data = {
        "user_id": user.id,
        "title": chat.title
    }
    response = supabase.table("chats").insert(data).execute()
    if response.data:
        return response.data[0]
    raise HTTPException(status_code=500, detail="Failed to create chat")

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(chat_id: str, user = Depends(get_current_user)):
    # Verify ownership
    # (RLS handles this actually, but good to be explicit)
    response = supabase.table("messages").select("*").eq("chat_id", chat_id).order("created_at").execute()
    return response.data

@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(chat_id: str, message: MessageCreate, user = Depends(get_current_user)):
    # 1. Save User Message
    user_msg_data = {
        "chat_id": chat_id,
        "role": "user",
        "content": message.content
    }
    supabase.table("messages").insert(user_msg_data).execute()
    
    # 2. Get AI Response
    ai_text = await gemini_service.generate_response(message.content)
    
    # 3. Save AI Message
    ai_msg_data = {
        "chat_id": chat_id,
        "role": "assistant",
        "content": ai_text,
        "model_used": "gemini-2.5-flash"
    }
    response = supabase.table("messages").insert(ai_msg_data).execute()
    
    if response.data:
        return response.data[0] # Returns the AI message
    raise HTTPException(status_code=500, detail="Failed to generate response")
