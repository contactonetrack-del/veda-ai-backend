import asyncio
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.orchestrator import orchestrator
from app.services.jira_service import jira_service

# Mock the Jira Service for testing if actual credentials fail/missing
# But here we want to test the routing logic mostly.

async def test_work_agent():
    print("Testing Work Agent Integration...")
    
    # 1. Test "Create Ticket" Intent
    query = "Create a Jira bug for 'Login button broken' with description 'User gets 500 error'"
    print(f"\n[Test 1] Query: '{query}'")
    
    # We expect 'work' intent and 'WorkAgent'
    result = await orchestrator.process_message(query, user_id="test_user", verify_facts=False)
    
    print(f"[Result] Intent: {result.get('intent')}")
    print(f"[Result] Agent: {result.get('agent_used')}")
    print(f"[Result] Response: {result.get('response')}")
    
    if result.get('intent') == 'work':
        print("[PASS] Intent Classification Passed")
    else:
        print("[FAIL] Intent Classification Failed")
        
    # 2. Test "Context" Intent
    query_context = "What is the status of the current sprint?"
    print(f"\n[Test 2] Query: '{query_context}'")
    
    result_ctx = await orchestrator.process_message(query_context, user_id="test_user", verify_facts=False)
    
    print(f"[Result] Intent: {result_ctx.get('intent')}")
    print(f"[Result] Agent: {result_ctx.get('agent_used')}")
    
    if result_ctx.get('intent') == 'work':
        print("[PASS] Intent Classification Passed")
    else:
        print("[FAIL] Intent Classification Failed")

if __name__ == "__main__":
    asyncio.run(test_work_agent())
