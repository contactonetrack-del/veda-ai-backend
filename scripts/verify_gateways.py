import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.model_router import model_router
from app.services.openrouter_service import openrouter_service
from app.services.xai_service import xai_service

async def verify_gateways():
    print("--- Verifying Advanced Gateway Integrations ---")
    print("================================================")
    
    # Check OpenRouter
    if openrouter_service.available:
        print("[OK] OpenRouter key detected.")
        try:
            response = await openrouter_service.generate_response(
                message="DeepSeek Check: Say 'DeepSeek Online'",
                model=openrouter_service.reasoning_model
            )
            print(f"[OK] OpenRouter Response: {response[:50]}...")
        except Exception as e:
            print(f"[FAIL] OpenRouter call failed: {e}")
    else:
        print("[WARN] OpenRouter key missing.")

    # Check xAI
    if xai_service.available:
        print("\n[OK] xAI key detected.")
        try:
            response = await xai_service.generate_response(
                message="Grok Check: Say 'Grok Online'",
                model=xai_service.default_model
            )
            print(f"[OK] xAI Response: {response[:50]}...")
        except Exception as e:
            print(f"[FAIL] xAI call failed: {e}")
    else:
        print("[WARN] xAI key missing.")

    # Test Router Auto-Logic
    print("\n--- Testing Model Router Logic ---")
    
    # 1. Complex -> OpenRouter / xAI
    print("Testing: Auto-Reasoning (OpenRouter/xAI Priority)")
    try:
        result = await model_router.generate(
            message="Analyze this complex nutritional chart for a keto diet.",
            provider="auto"
        )
        print(f"[OK] Routed to: {result.get('provider')}")
        print(f"   Model: {result.get('model')}")
    except Exception as e:
        print(f"[FAIL] Auto-Reasoning failed: {e}")

    # 2. Fast -> Groq / xAI
    print("\nTesting: Auto-Fast (Groq/xAI Priority)")
    try:
        result = await model_router.generate(
            message="Hi there!",
            provider="auto",
            fast=True
        )
        print(f"[OK] Routed to: {result.get('provider')}")
        print(f"   Model: {result.get('model')}")
    except Exception as e:
        print(f"[FAIL] Auto-Fast failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_gateways())
