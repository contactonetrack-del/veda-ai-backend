"""
Embeddings service using Google Gemini Embeddings API
Converts text to 768-dimensional vectors for semantic search
"""
from google import genai
from app.core.config import get_settings

settings = get_settings()
client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def generate_embedding(text: str) -> list[float]:
    """
    Generate embedding vector for given text
    Returns 768-dimensional vector
    """
    try:
        result = client.models.embed_content(
            model='models/text-embedding-004',
            content=text
        )
        return result.embeddings[0].values
    except Exception as e:
        print(f"Embedding Error: {e}")
        # Return zero vector as fallback
        return [0.0] * 768
