from faster_whisper import WhisperModel
import os

print("⏳ Downloading Whisper base model (140MB)...")
try:
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print("✅ Model cached at default locations.")
    print("   Ready for Hindi transcription")
except Exception as e:
    print(f"❌ Failed to download model: {e}")
