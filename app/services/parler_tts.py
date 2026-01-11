"""
Multi-Language TTS Service for VEDA AI
Supports 10 Indian languages using Facebook MMS models
"""
import os
import logging
import torch
import soundfile as sf
import asyncio
from typing import Optional, Dict, Generator
from transformers import VitsModel, AutoTokenizer

# Language to MMS model mapping
# Note: Some languages need script-specific variants
LANGUAGE_MODELS = {
    "hi": "facebook/mms-tts-hin",                    # Hindi
    "bn": "facebook/mms-tts-ben",                    # Bengali
    "te": "facebook/mms-tts-tel",                    # Telugu
    "mr": "facebook/mms-tts-mar",                    # Marathi
    "ta": "facebook/mms-tts-tam",                    # Tamil
    "ur": "facebook/mms-tts-hin",                    # Urdu -> Hindi fallback (script issue)
    "kn": "facebook/mms-tts-kan",                    # Kannada
    "pa": "facebook/mms-tts-pan",                    # Punjabi
    "or": "facebook/mms-tts-ory",                    # Odia (correct code is ory)
    "as": "facebook/mms-tts-asm",                    # Assamese
    "gui": "facebook/mms-tts-guj",                   # Gujarati
    "ml": "facebook/mms-tts-mal",                    # Malayalam
    "sa": "facebook/mms-tts-san",                    # Sanskrit
    "ne": "facebook/mms-tts-nep",                    # Nepali
    "mai": "facebook/mms-tts-mai",                   # Maithili (NEW)
    "sat": "facebook/mms-tts-sat",                   # Santali (NEW)
    "kas": "facebook/mms-tts-kas",                   # Kashmiri (NEW)
    "kok": "facebook/mms-tts-kok",                   # Konkani (NEW)
    "snd": "facebook/mms-tts-snd",                   # Sindhi (NEW)
    "mni": "facebook/mms-tts-mni",                   # Manipuri (NEW)
    "doi": "facebook/mms-tts-doi",                   # Dogri (NEW)
    "brx": "facebook/mms-tts-brx",                   # Bodo (SCHEDULED - 100% Goal)
    "hne": "facebook/mms-tts-hne",                   # Chhattisgarhi (MAJOR - 99% Goal)
    "wsg": "facebook/mms-tts-wsg",                   # Gondi (MAJOR - 99% Goal)
    "bho": "facebook/mms-tts-hin",                   # Bhojpuri -> Hindi fallback
    # English fallback
    "en": "facebook/mms-tts-eng",                    # English
}

# Language display names
LANGUAGE_NAMES = {
    "hi": "Hindi", "bn": "Bengali", "te": "Telugu", "mr": "Marathi",
    "ta": "Tamil", "ur": "Urdu", "kn": "Kannada", "pa": "Punjabi",
    "or": "Odia", "as": "Assamese", "gui": "Gujarati", "ml": "Malayalam",
    "sa": "Sanskrit", "ne": "Nepali", "mai": "Maithili", "sat": "Santali",
    "kas": "Kashmiri", "kok": "Konkani", "snd": "Sindhi", "mni": "Manipuri",
    "doi": "Dogri", "brx": "Bodo", "hne": "Chhattisgarhi", "wsg": "Gondi",
    "bho": "Bhojpuri", "en": "English"
}

class MultiLanguageTTSService:
    """
    Multi-language TTS service with dynamic model loading.
    Loads models on-demand to save memory.
    """
    
    def __init__(self, default_language: str = "hi", device: str = None):
        self.logger = logging.getLogger(__name__)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.default_language = default_language
        
        # Cache for loaded models (language -> (model, tokenizer))
        self.model_cache: Dict[str, tuple] = {}
        self.max_cache_size = 3  # Keep max 3 models in memory
        
        # Preload default language
        self._load_model(default_language)
    
    def _load_model(self, language: str):
        """Load model for a specific language"""
        if language in self.model_cache:
            return self.model_cache[language]
        
        model_id = LANGUAGE_MODELS.get(language, LANGUAGE_MODELS["hi"])
        lang_name = LANGUAGE_NAMES.get(language, language)
        
        try:
            self.logger.info(f"Loading TTS model for {lang_name}: {model_id}")
            
            model = VitsModel.from_pretrained(model_id).to(self.device)
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            
            # Manage cache size
            if len(self.model_cache) >= self.max_cache_size:
                # Remove oldest model (first key)
                oldest = next(iter(self.model_cache))
                del self.model_cache[oldest]
                self.logger.info(f"Evicted {oldest} from cache")
            
            self.model_cache[language] = (model, tokenizer)
            self.logger.info(f"TTS model for {lang_name} loaded successfully")
            return model, tokenizer
            
        except Exception as e:
            self.logger.error(f"Failed to load TTS model for {lang_name}: {e}")
            # Fallback to Hindi
            if language != "hi":
                self.logger.info("Falling back to Hindi TTS")
                return self._load_model("hi")
            raise
    
    def get_model(self, language: str):
        """Get model and tokenizer for language"""
        if language not in self.model_cache:
            self._load_model(language)
        return self.model_cache.get(language)
    
    def synthesize(self, text: str, language: str, output_path: str) -> bool:
        """
        Synthesize text to speech for any supported language.
        """
        try:
            model, tokenizer = self.get_model(language)
            
            self.logger.info(f"Synthesizing {LANGUAGE_NAMES.get(language, language)}: {text[:50]}...")
            inputs = tokenizer(text, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                output = model(**inputs).waveform
            
            audio_data = output.cpu().numpy().squeeze()
            
            # MMS output sample rate is 16000Hz
            sf.write(output_path, audio_data, 16000)
            self.logger.info(f"Audio saved to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Synthesis failed: {e}")
            return False
    
    def synthesize_streaming(self, text: str, language: str) -> Generator[bytes, None, None]:
        """
        Stream synthesized audio in chunks.
        Yields audio data in WAV format chunks.
        """
        try:
            model, tokenizer = self.get_model(language)
            
            self.logger.info(f"Streaming {LANGUAGE_NAMES.get(language, language)}: {text[:50]}...")
            inputs = tokenizer(text, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                output = model(**inputs).waveform
            
            audio_data = output.cpu().numpy().squeeze()
            
            # Convert to bytes and yield in chunks
            import io
            import wave
            
            # Create WAV in memory
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(16000)
                wf.writeframes((audio_data * 32767).astype('int16').tobytes())
            
            # Yield in chunks
            buffer.seek(0)
            chunk_size = 4096
            while True:
                chunk = buffer.read(chunk_size)
                if not chunk:
                    break
                yield chunk
                
        except Exception as e:
            self.logger.error(f"Streaming synthesis failed: {e}")
            yield b''
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Return dict of supported language codes and names"""
        return LANGUAGE_NAMES.copy()
    
    def get_status(self) -> Dict:
        """Get service status"""
        return {
            "status": "ready",
            "device": self.device,
            "cached_languages": list(self.model_cache.keys()),
            "supported_languages": list(LANGUAGE_MODELS.keys()),
            "cache_size": len(self.model_cache),
            "max_cache_size": self.max_cache_size
        }


# Singleton instance
_tts_service = None

def get_tts_service() -> MultiLanguageTTSService:
    global _tts_service
    if _tts_service is None:
        _tts_service = MultiLanguageTTSService()
    return _tts_service


# Legacy compatibility - for existing code that passes model_id
class ParlerTTSService(MultiLanguageTTSService):
    """Legacy wrapper for backward compatibility"""
    def __init__(self, model_id: str = "facebook/mms-tts-hin", device: str = None):
        # Extract language from model_id
        lang = "hi"
        for code, mid in LANGUAGE_MODELS.items():
            if mid == model_id:
                lang = code
                break
        super().__init__(default_language=lang, device=device)
    
    def synthesize(self, text: str, description: str, output_path: str) -> bool:
        # Ignore description, use default language
        return super().synthesize(text, self.default_language, output_path)
