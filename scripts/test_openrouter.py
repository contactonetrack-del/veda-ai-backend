import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.model_router import model_router
from app.services.openrouter_service import openrouter_service

async def verify_openrouter():
    print("--- Verifying OpenRouter Integration ---")
    print("========================================")
    
    # Check if key is available
    if not openrouter_service.available:
        print("[ERROR] OpenRouter API key not detected in settings.")
        return

    print("[OK] OpenRouter key detected.")
    
    # Test 1: Direct Service Call (Reasoning)
    print("\nTesting: Direct Model Call (DeepSeek R1)")
    try:
        response = await openrouter_service.generate_response(
            message="Explain quantum entanglement in 2 sentences.",
            model=openrouter_service.reasoning_model
        )
        print(f"[OK] Response received: {response[:100]}...")
    except Exception as e:
        print(f"[FAIL] Direct call failed: {e}")

    # Test 2: Model Router Auto-Routing (Complex)
    print("\nTesting: Model Router Priority (Auto-Reasoning)")
    try:
        result = await model_router.generate(
            message="Analyze this complex medical scenario: A patient with high blood pressure and chronic fatigue.",
            provider="auto"
        )
        print(f"[OK] Routed to: {result.get('provider')}")
        print(f"   Model: {result.get('model')}")
        print(f"   Response: {result.get('response')[:100]}...")
    except Exception as e:
        print(f"[FAIL] Router test failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_openrouter())
