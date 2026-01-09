import google.generativeai as genai
from app.core.config import get_settings

settings = get_settings()

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Using the model configured in previous steps
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def generate_response(self, message: str, history: list = []):
        try:
            # Convert simple history format if needed, or just send prompt for now
            # For a MVP stateless call:
            response = self.model.generate_content(message)
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "I apologize, but I'm having trouble connecting to my brain right now. Please try again in a moment."

gemini_service = GeminiService()
