from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "VEDA AI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # AI Models
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""  # Optional: For LLaMA via Groq
    
    # Web Search APIs (Phase 1: Perplexity-class)
    BRAVE_API_KEY: str = ""  # Primary: 2,000 free searches/month
    TAVILY_API_KEY: str = ""  # Fallback: 100 free calls
    
    # Ollama Cloud
    OLLAMA_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
