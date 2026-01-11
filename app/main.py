from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth, chat, transcribe, vision, orchestrator, local_llm, reasoning, experts, browser, knowledge, voice

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core routes
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chats", tags=["chats"])
app.include_router(transcribe.router, prefix=f"{settings.API_V1_STR}/audio", tags=["audio"])
app.include_router(vision.router, prefix=f"{settings.API_V1_STR}/vision", tags=["vision"])
app.include_router(orchestrator.router, prefix=f"{settings.API_V1_STR}/orchestrator", tags=["orchestrator"])

# Phase 1-3: Local AI Routes
app.include_router(local_llm.router, prefix=f"{settings.API_V1_STR}/local-llm", tags=["local-llm"])
app.include_router(reasoning.router, prefix=f"{settings.API_V1_STR}/reasoning", tags=["reasoning"])
app.include_router(experts.router, prefix=f"{settings.API_V1_STR}/experts", tags=["experts"])
app.include_router(browser.router, prefix=f"{settings.API_V1_STR}/browser", tags=["browser"])

# Phase 4: Knowledge Base & RAG
app.include_router(knowledge.router, prefix=f"{settings.API_V1_STR}/knowledge", tags=["knowledge"])

# Phase 7: Voice Integration
app.include_router(voice.router)



@app.get("/")
def root():
    return {"message": "VEDA AI Backend Running", "version": settings.VERSION}

@app.get("/health")
def health_check():
    return {"status": "ok"}
