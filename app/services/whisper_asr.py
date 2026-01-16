import os
import logging
from typing import Tuple, List, Dict, Any

# Check if faster-whisper is available
try:
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    WhisperModel = None
    logging.warning("faster-whisper not installed. ASR features will be disabled.")

# Model size from env (tiny=fastest, base=balanced, small=better accuracy)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")  # Changed to tiny for speed

class WhisperASRService:
    def __init__(self, model_size: str = None, device: str = "cpu", compute_type: str = "int8"):
        self.logger = logging.getLogger(__name__)
        self.model_size = model_size or WHISPER_MODEL
        self.device = device
        self.compute_type = compute_type
        self.model = None
        self.is_available = HAS_WHISPER
        
        # Only load model if faster-whisper is available
        if self.is_available:
            self._load_model()

    def _load_model(self):
        if not HAS_WHISPER or WhisperModel is None:
            self.logger.warning("Whisper not available - skipping model load")
            return
            
        try:
            self.logger.info(f"Loading Whisper model: {self.model_size} (device={self.device}, compute_type={self.compute_type})")
            self.model = WhisperModel(
                self.model_size, 
                device=self.device, 
                compute_type=self.compute_type
            )
            self.logger.info("Whisper model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            self.is_available = False

    def transcribe(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        Returns a dict with transcript, detected_language, and confidence.
        """
        if not self.is_available or not self.model:
            return {"error": "Whisper ASR not available. faster-whisper is not installed."}

        try:
            self.logger.info(f"Transcribing: {audio_path}")
            # Enable VAD filtering to skip silence (faster processing)
            # Use beam_size=1 for faster greedy decoding (2x speedup)
            segments, info = self.model.transcribe(
                audio_path, 
                language=language,
                beam_size=1,      # Greedy decoding
                vad_filter=True,  # Skip silence
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            transcript = " ".join([segment.text for segment in segments])
            
            return {
                "text": transcript.strip(),
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration
            }
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return {"error": str(e)}

# Singleton instance - safe to create even without faster-whisper
asr_service = WhisperASRService()
