from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "VEDA AI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # AI Models
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    VITE_GROQ_API_KEY: str = ""  # For frontend usage via backend proxy
    
    # Web Search APIs (Phase 1: Perplexity-class)
    BRAVE_API_KEY: str = ""  # Primary: 2,000 free searches/month
    TAVILY_API_KEY: str = ""  # Fallback: 100 free calls
    
    # Ollama Cloud
    OLLAMA_API_KEY: str = ""
    
    # OpenRouter
    OPENROUTER_API_KEY: str = ""
    
    # xAI
    XAI_API_KEY: str = ""

    # Jira MCP Integration
    JIRA_HOST: str = "https://onetrack.atlassian.net"
    JIRA_USER_EMAIL: str = ""
    JIRA_API_TOKEN: str = ""
    JIRA_PROJECT_KEY: str = "DEV"
    
    # Slack Integration
    SLACK_BOT_TOKEN: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
