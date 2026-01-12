import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings
from app.services.ollama_service import ollama_service

async def test_cloud_connection():
    print("🚀 Veda AI Cloud Connection Test")
    print("===============================")
    
    settings = get_settings()
    
    # Check 1: API Key Presence
    if settings.OLLAMA_API_KEY:
        print(f"✅ Ollama API Key Detected: {settings.OLLAMA_API_KEY[:5]}...{settings.OLLAMA_API_KEY[-5:]}")
    else:
        print("❌ Ollama API Key MISSING in settings!")
        return

    # Check 2: Service Initialization
    if ollama_service.is_available:
        print("✅ Ollama Service Initialized (Cloud Mode)")
    else:
        print("❌ Ollama Service Initialization FAILED")
        return

    # Check 3: Simple Inference
    print("\nAttempting Cloud Interface (Simple)...")
    try:
        response = await ollama_service.invoke(
            prompt="Hello! Are you running on the cloud?",
            model_type="fast",
            max_tokens=50
        )
        print(f"Response: {response.get('response')}")
        print(f"Provider: {response.get('cloud_provider', 'local')}")
        print("✅ Simple Inference Success")
    except Exception as e:
        print(f"❌ Simple Inference Failed: {e}")

    # Check 4: Deep Reasoning (DeepSeek R1)
    print("\nAttempting Deep Reasoning (DeepSeek R1)...")
    try:
        response = await ollama_service.invoke(
            prompt="What is heavier, a kilo of feathers or a kilo of lead? Explain briefly.",
            model_type="reasoning",
            max_tokens=200
        )
        print(f"Response: {response.get('response')}")
        print(f"Model Used: {response.get('model_used')}")
        print("✅ Deep Reasoning Success")
    except Exception as e:
        print(f"❌ Deep Reasoning Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_cloud_connection())
