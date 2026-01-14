import asyncio
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.model_router import model_router
from app.services.jira_service import jira_service

async def test_jira_write():
    print("Testing Jira Write Logic...")
    
    if not jira_service.available:
        print("Jira Service Unavailable. Aborting.")
        return

    # Simulate User Request
    test_query = "Create a task called 'Test Task from Veda AI' with description 'This is an automated test.'"
    
    print(f"\n[Action] User says: '{test_query}'")
    
    # We expect the model_router to catch 'create' + 'task', 
    # inject the instruction, and parse the response.
    
    # Note: Since we are using REAL LLMs in the router, this test *might* cost money or fail if LLM refuses.
    # But checking internal logic:
    
    # We can mock the response parsing logic by forcing a specific message if we wanted unit tests.
    # But for this integration test, let's see if the keywords trigger the injection.
    
    try:
        # We will simulate the internal generation to avoid waiting for LLM 
        # OR we just run it if user is okay with 1 call. 
        # Given the "Go ahead", we run it.
        
        result = await model_router.generate(test_query)
        
        print(f"\n[Result] Provider: {result.get('provider')}")
        print(f"[Result] Full Response:\n{result.get('response')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_jira_write())
