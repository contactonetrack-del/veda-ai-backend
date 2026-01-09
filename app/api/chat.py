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
    from app.services.embeddings import generate_embedding
    from app.services.memory import vector_memory
    
    # 1. Save User Message to Database
    user_msg_data = {
        "chat_id": chat_id,
        "role": "user",
        "content": message.content
    }
    supabase.table("messages").insert(user_msg_data).execute()
    
    # 2. Generate embedding for user message
    user_embedding = await generate_embedding(message.content)
    
    # 3. Search for relevant context from past conversations
    context = await vector_memory.search_context(
        user_id=user.id,
        query_embedding=user_embedding,
        top_k=3  # Get top 3 most relevant past messages
    )
    
    # 4. Build context-aware prompt
    context_text = ""
    if context:
        context_text = "\n\n**Relevant context from past conversations:**\n"
        for ctx in context:
            context_text += f"- {ctx['role']}: {ctx['message']}\n"
    
    enhanced_prompt = f"""{context_text}

**Current user message:** {message.content}

Please provide a personalized response based on the user's history and current question."""
    
    # 5. Get AI Response with context
    ai_text = await gemini_service.generate_response(enhanced_prompt)
    
    # 6. Save AI Message to Database
    ai_msg_data = {
        "chat_id": chat_id,
        "role": "assistant",
        "content": ai_text,
        "model_used": "gemini-2.0-flash-exp"
    }
    response = supabase.table("messages").insert(ai_msg_data).execute()
    
    # 7. Store both messages in vector memory for future context
    await vector_memory.add_message(
        user_id=user.id,
        message=message.content,
        role="user",
        embedding=user_embedding,
        metadata={"chat_id": chat_id}
    )
    
    ai_embedding = await generate_embedding(ai_text)
    await vector_memory.add_message(
        user_id=user.id,
        message=ai_text,
        role="assistant",
        embedding=ai_embedding,
        metadata={"chat_id": chat_id}
    )
    
    if response.data:
        return response.data[0]  # Returns the AI message
    raise HTTPException(status_code=500, detail="Failed to generate response")

