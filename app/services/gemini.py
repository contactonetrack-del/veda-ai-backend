import httpx
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
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate_response(self, message: str, history: list = [], language: str = "en"):
            if not self.api_key:
                return "Error: Gemini API Key not configured"

            # Build history text
            history_text = ""
            for msg in history[-5:]:
                role = "User" if msg.get("role") == "user" else "Assistant"
                history_text += f"\n{role}: {msg.get('content')}"

            full_prompt = f"{VEDA_SYSTEM_INSTRUCTION}\n\nRecent Conversation:{history_text}\n\nUser: {message}\n\nAssistant:"
            
            try:
                # Use Gemini 1.5 Flash via REST API
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.base_url}/gemini-1.5-flash:generateContent?key={self.api_key}",
                        json={
                            "contents": [{
                                "parts": [{"text": full_prompt}]
                            }]
                        }
                    )
                    
                    if response.status_code != 200:
                        return f"Error: Gemini API {response.status_code} - {response.text}"
                        
                    data = response.json()
                    if "candidates" in data and data["candidates"]:
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        return "Error: No response from Gemini"
                        
            except Exception as e:
                return f"Error calling Gemini: {str(e)}"

gemini_service = GeminiService()
