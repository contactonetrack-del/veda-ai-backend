from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth, chat, transcribe, vision

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

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chats", tags=["chats"])
app.include_router(transcribe.router, prefix=f"{settings.API_V1_STR}/audio", tags=["audio"])
app.include_router(vision.router, prefix=f"{settings.API_V1_STR}/vision", tags=["vision"])

@app.get("/")
def root():
    return {"message": "VEDA AI Backend Running", "version": settings.VERSION}

@app.get("/health")
def health_check():
    return {"status": "ok"}
