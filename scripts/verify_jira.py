import asyncio
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.model_router import model_router
from app.services.jira_service import jira_service

async def test_jira_integration():
    print("Testing Jira Integration...")
    
    # 1. Check Service Availability
    if not jira_service.available:
        print("Jira Service is NOT available. Check settings.")
        return

    print("Jira Service is available.")
    
    # 2. Test Context Fetch
    print("\n[Action] Fetching Project Context...")
    context = jira_service.get_project_context()
    print(f"[Result] Context Preview:\n{context[:200]}...") # Show first 200 chars
    
    # 3. Test Routing Logic (Simulation)
    test_query = "What is the status of the current sprint?"
    print(f"\n[Action] Sending Query: '{test_query}'")
    
    # Note: We are mocking the generation to avoid actual API costs/calls if possible, 
    # but here we want to see the system prompt change.
    # Since we can't easily inspect internal state without a debugger, 
    # we'll look for the print statement "📊 Injecting Jira Context..." in stdout.
    
    try:
        # We will actually call it, relying on the 'auto' routing.
        # It should pick Groq/Gemini and include the context.
        result = await model_router.generate(test_query)
        print(f"\n[Result] Response Provider: {result.get('provider')}")
        print(f"[Result] Response: {result.get('response')[:100]}...")
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")

if __name__ == "__main__":
    asyncio.run(test_jira_integration())
