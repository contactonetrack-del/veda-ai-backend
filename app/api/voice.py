"""
Voice WebSocket API
Real-time voice streaming endpoint for VEDA AI
Supports 10 Indian languages with streaming audio
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import asyncio
import os
import tempfile
import logging
import wave
import json

from app.services.whisper_asr import asr_service
from app.services.parler_tts import get_tts_service, LANGUAGE_NAMES, LANGUAGE_MODELS
from app.services.voice_router import voice_router

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])
logger = logging.getLogger(__name__)

# Store active connections
active_connections: list[WebSocket] = []


@router.websocket("/ws")
async def voice_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice interaction.
    
    Protocol:
    1. Client sends audio chunks (16kHz, 16-bit PCM)
    2. Server sends back JSON messages with transcript/response
    3. Server streams audio chunks for TTS output
    
    Supported Languages: Hindi, Bengali, Telugu, Marathi, Tamil, Urdu, Kannada, Punjabi, Odia, Bhojpuri
    """
    await websocket.accept()
    active_connections.append(websocket)
    logger.info("Voice WebSocket connected")
    
    audio_buffer = bytearray()
    user_id = "voice_user_default"
    preferred_language = None  # Auto-detect
    
    try:
        while True:
            data = await websocket.receive()
            
            if "bytes" in data:
                audio_buffer.extend(data["bytes"])
                # Buffer until end_stream (for File Uploads like M4A)
                    
            elif "text" in data:
                command = json.loads(data["text"])
                
                if command.get("type") == "end_stream":
                    if len(audio_buffer) > 0:
                        await process_audio_streaming(websocket, audio_buffer, user_id, preferred_language)
                    audio_buffer.clear()
                    
                elif command.get("type") == "set_user":
                    user_id = command.get("user_id", user_id)
                    
                elif command.get("type") == "set_language":
                    # Force specific output language
                    preferred_language = command.get("language")
                    logger.info(f"Output language set to: {preferred_language}")
                    
    except WebSocketDisconnect:
        logger.info("Voice WebSocket disconnected")
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)


async def process_audio_streaming(websocket: WebSocket, audio_buffer: bytearray, user_id: str, preferred_language: str = None):
    """
    Process audio with streaming TTS output.
    Uses multi-language TTS based on detected/preferred language.
    """
    tmp_path = None
    
    try:
        # 1. Save audio to temp file (Direct write, handle container formats like M4A/WebM)
        with tempfile.NamedTemporaryFile(suffix=".audio", delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(audio_buffer)
            
        # 2. Transcribe with Whisper (auto language detection)
        logger.info("Transcribing audio...")
        result = asr_service.transcribe(tmp_path)
        
        if "error" in result:
            await websocket.send_json({"type": "error", "message": result["error"]})
            return
            
        transcript = result["text"]
        detected_language = result["language"]
        
        # Use preferred language for TTS output, or detected language
        output_language = preferred_language or detected_language
        
        # Map Whisper language codes to our TTS codes
        language_map = {
            "hindi": "hi", "hi": "hi",
            "bengali": "bn", "bn": "bn",
            "telugu": "te", "te": "te",
            "marathi": "mr", "mr": "mr",
            "tamil": "ta", "ta": "ta",
            "urdu": "ur", "ur": "ur",
            "kannada": "kn", "kn": "kn",
            "punjabi": "pa", "pa": "pa",
            "oriya": "or", "or": "or",
            "assamese": "as", "as": "as",
            "gujarati": "gui", "gu": "gui",
            "malayalam": "ml", "ml": "ml",
            "sanskrit": "sa", "sa": "sa",
            "nepali": "ne", "ne": "ne",
            "maithili": "mai", "mai": "mai",
            "santali": "sat", "sat": "sat",
            "kashmiri": "kas", "kas": "kas",
            "konkani": "kok", "kok": "kok",
            "sindhi": "snd", "snd": "snd",
            "manipuri": "mni", "mni": "mni",
            "dogri": "doi", "doi": "doi",
            "bodo": "brx", "brx": "brx",
            "chhattisgarhi": "hne", "hne": "hne",
            "gondi": "wsg", "wsg": "wsg",
            "bhojpuri": "bho", "bho": "bho",
            "english": "en", "en": "en"
        }
        tts_language = language_map.get(output_language.lower(), "hi")
        
        # Send transcript to client
        await websocket.send_json({
            "type": "transcript",
            "text": transcript,
            "language": detected_language,
            "tts_language": tts_language,
            "confidence": result.get("language_probability", 0.0)
        })
        
        # 3. Route to domain expert
        logger.info(f"Routing to expert: {transcript[:50]}...")
        expert_result = await voice_router.route_query(transcript, detected_language, user_id)
        
        if "error" in expert_result:
            await websocket.send_json({"type": "error", "message": expert_result["error"]})
            return
            
        response_text = expert_result["response_text"]
        
        # Send response text to client
        await websocket.send_json({
            "type": "response",
            "text": response_text,
            "language": tts_language
        })
        
        # 4. Stream synthesized audio
        logger.info(f"Streaming TTS in {LANGUAGE_NAMES.get(tts_language, tts_language)}...")
        tts = get_tts_service()
        
        # Send audio start marker
        await websocket.send_json({"type": "audio_start", "language": tts_language})
        
        # Stream audio chunks
        for chunk in tts.synthesize_streaming(response_text, tts_language):
            if chunk:
                await websocket.send_bytes(chunk)
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)
        
        # Send audio end marker
        await websocket.send_json({"type": "audio_end"})
        
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        # Cleanup temp file
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/health")
async def voice_health():
    """Health check for voice services"""
    whisper_ok = asr_service.model is not None
    tts_status = {}
    
    try:
        tts = get_tts_service()
        tts_status = tts.get_status()
    except Exception as e:
        tts_status = {"error": str(e)}
        
    return {
        "status": "ok" if whisper_ok else "degraded",
        "whisper_asr": {
            "status": "ready" if whisper_ok else "not_loaded",
            "model": asr_service.model_size if whisper_ok else None
        },
        "tts": tts_status,
        "active_connections": len(active_connections)
    }


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for voice interaction"""
    return {
        "supported_languages": [
            {"code": code, "name": name, "tts_model": LANGUAGE_MODELS.get(code)}
            for code, name in LANGUAGE_NAMES.items()
        ],
        "default": "hi",
        "note": "Bhojpuri uses Hindi TTS as fallback"
    }
