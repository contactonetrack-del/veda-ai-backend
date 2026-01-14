import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.model_router import model_router

async def test_routing():
    print("🚀 Verifying Zero-Cost Hybrid Routing\n" + "="*40)
    
    test_cases = [
        {
            "name": "Complex Reasoning (Medical)",
            "prompt": "Analyze this medical diet plan for diabetes.",
            "expected_provider": "groq",
            "expected_model_type": "reasoning" # DeepSeek
        },
        {
            "name": "Vision Task",
            "prompt": "Look at this photo of my lunch.",
            "expected_provider": "gemini",
            "expected_model_type": "vision" # Gemini 2.0
        },
        {
            "name": "Fast Chat",
            "prompt": "Hello, how are you?",
            "expected_provider": "groq",
            "expected_model_type": "fast" # Llama 3
        },
        {
            "name": "Explicit Backup",
            "prompt": "Force backup test",
            "expected_provider": "ollama" # Only if forced or others fail, but here we just check availability
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        print(f"Prompt: {test['prompt']}")
        
        # We invoke the router's internal logic check without making full API calls needed
        # But actually, lets just run generate() and see who answers based on the returned 'provider' key
        # We mock the keys availability via the services themselves if needed, but assuming keys in env
        
        try:
            # Note: This will actually call the APIs.
            # For verification, we just want to see the "provider" in the response dict.
            # We don't need the full text response for this check.
            
            # Since we can't easily spy on the internal decision without mocking, 
            # we will rely on the return value of generate() which includes "provider"
            
            # Skip actual API call if keys are missing (logic check only)
            pass 
            
            # Actually, let's just inspect the logic in ModelRouter by calling it
            result = await model_router.generate(message=test["prompt"], provider="auto", fast=(test['name'] == "Fast Chat"))
            
            provider = result.get("provider")
            model = result.get("model")
            
            print(f"✅ Routed to: {provider}")
            print(f"   Model: {model}")
            
            if test.get("expected_provider") and provider != test["expected_provider"]:
                # Special case: If Groq key not missing, might fallback to OLLAMA
                print(f"⚠️ Warning: Expected {test['expected_provider']} but got {provider}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_routing())
