from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai
from app.core.config import get_settings
import base64
import tempfile
import os

settings = get_settings()
router = APIRouter()

class TranscribeRequest(BaseModel):
    audio_base64: str
    language: str = "en"

class TranscribeResponse(BaseModel):
    text: str
    success: bool

# Language code mapping for transcription hints
LANGUAGE_HINTS = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil", 
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "gu": "Gujarati",
    "bn": "Bengali",
    "or": "Odia",
    "pa": "Punjabi",
    "bho": "Bhojpuri (Hindi dialect)",
}

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(request: TranscribeRequest):
    """
    Transcribe audio using Gemini's multimodal capabilities.
    Accepts base64 encoded audio and returns transcribed text.
    """
    try:
        # Decode the base64 audio
        audio_data = base64.b64decode(request.audio_base64)
        
        # Save to temporary file (Gemini needs a file path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            # Initialize Gemini client
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Get language hint
            lang_hint = LANGUAGE_HINTS.get(request.language, "English")
            
            # Upload the audio file
            uploaded_file = client.files.upload(file=temp_path)
            
            # Create transcription prompt
            prompt = f"""Please transcribe the following audio file. 
The audio is likely in {lang_hint}. 
Transcribe exactly what is spoken, preserving the original language.
If the audio is unclear or empty, respond with an empty string.
Only output the transcription, nothing else."""

            # Use Gemini to transcribe
            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=[
                    prompt,
                    uploaded_file
                ]
            )
            
            transcribed_text = response.text.strip() if response.text else ""
            
            # Clean up: delete uploaded file from Gemini
            try:
                client.files.delete(name=uploaded_file.name)
            except:
                pass  # Ignore cleanup errors
            
            return TranscribeResponse(text=transcribed_text, success=True)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        print(f"Transcription error: {e}")
        return TranscribeResponse(text="", success=False)
