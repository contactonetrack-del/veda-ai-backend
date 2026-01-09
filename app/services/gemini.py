from google import genai
from google.genai import types
from app.core.config import get_settings

settings = get_settings()

class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def generate_response(self, message: str, history: list = []):
        try:
            # Simple stateless call for now
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=message
            )
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "I apologize, but I'm having trouble connecting to my brain right now. Please try again in a moment."

gemini_service = GeminiService()
