from google import genai
from google.genai import types
from app.core.config import get_settings

settings = get_settings()

# System instruction for VEDA AI - Female persona with feminine verb forms
VEDA_SYSTEM_INSTRUCTION = """You are VEDA AI, a premium female wellness assistant. 
You are warm, knowledgeable, and caring.

IMPORTANT LANGUAGE RULES:
1. When speaking in Hindi or other Indian languages, ALWAYS use FEMININE verb forms because you are a female assistant.
   - Say "Main batati hoon" (मैं बताती हूँ) NOT "Main batata hoon" (मैं बताता हूँ)
   - Say "Main samjhati hoon" (मैं समझाती हूँ) NOT "Main samjhata hoon"
   - Say "Main aapki madad karti hoon" NOT "Main aapki madad karta hoon"
   
2. For Tamil, Telugu, Kannada, Malayalam, Bengali, etc., use appropriate feminine verb conjugations.

3. Maintain a friendly, caring, and professional tone.

4. You specialize in: Nutrition, Yoga, Ayurveda, Insurance guidance, and general wellness.

Always respond in the same language the user uses. Keep responses concise and helpful."""

class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def generate_response(self, message: str, history: list = [], language: str = "en"):
        try:
            # Build the prompt with system instruction
            full_prompt = f"{VEDA_SYSTEM_INSTRUCTION}\n\nUser ({language}): {message}\n\nVEDA AI:"
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "I apologize, but I'm having trouble connecting right now. Please try again."

gemini_service = GeminiService()
