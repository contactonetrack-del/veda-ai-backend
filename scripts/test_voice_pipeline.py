import os
import asyncio
import logging
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.whisper_asr import asr_service
from app.services.parler_tts import get_tts_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_voice_pipeline():
    test_text = "नमस्ते, मेरा नाम वेद है। मैं आपकी कैसे मदद कर सकता हूँ?"
    test_description = "A male Hindi speaker with a clear and helpful tone."
    audio_output = "scripts/test_hindi_voice.wav"

    print("\n--- 🟢 Starting Voice Pipeline Test ---")

    # 1. Test TTS (Synthesis)
    print("\n1️⃣ Step 1: Testing Parler-TTS (Hindi Synthesis)...")
    try:
        from transformers import AutoTokenizer
        tts = get_tts_service()
        success = tts.synthesize(test_text, test_description, audio_output)
        if success:
            print(f"✅ TTS Success! Audio saved to {audio_output}")
        else:
            print("❌ TTS Failed!")
            return
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return

    # 2. Test ASR (Transcription)
    print("\n2️⃣ Step 2: Testing Whisper ASR (Hindi Transcription)...")
    try:
        result = asr_service.transcribe(audio_output, language="hi")
        if "error" in result:
            print(f"❌ ASR Error: {result['error']}")
        else:
            print(f"✅ ASR Success!")
            print(f"   Detected Language: {result['language']} (Prob: {result['language_probability']:.2f})")
            print(f"   Transcript: {result['text']}")
    except Exception as e:
        print(f"❌ ASR Error: {e}")

    print("\n--- 🏁 Voice Pipeline Test Complete ---")

if __name__ == "__main__":
    asyncio.run(test_voice_pipeline())
