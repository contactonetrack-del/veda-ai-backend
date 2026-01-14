
import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.deep_research import deep_research_agent
from app.services.web_search import web_search

async def test_deep_research():
    print("[TEST] Testing Deep Research Agent (Target: 100+ Sources)...")
    
    # Check availability
    if not web_search.is_available:
        print("[SKIP] Web search not available. Skipping test.")
        return

    query = "impact of quantum computing on encryption standards by 2030"
    print(f"\n[TEST] Running Research Task: '{query}'")
    print("[INFO] This may take 30-60 seconds due to 6-step deep analysis...")
    
    try:
        result = await deep_research_agent.process(query)
        
        if result.get("success"):
            print("\n[OK] Research Complete!")
            print(f"[INFO] Total Sources Analyzed: {result.get('source_count')}")
            print(f"[INFO] Report Length: {len(result.get('response'))} chars")
            
            print("\n--- EXECUTIVE SUMMARY PREVIEW ---")
            print(result.get("response")[:500] + "...")
            print("\n--- TOP SOURCES ---")
            for i, s in enumerate(result.get("sources", [])[:3], 1):
                print(f"{i}. {s['title']} ({s['url']})")
                
            if result.get("source_count", 0) > 50:
                print("\n[PASS] Source count exceeds 50 (High Depth)")
            else:
                print(f"\n[WARN] Source count {result.get('source_count')} is low. Check API limits.")
                
        else:
            print(f"[FAIL] Agent failed: {result}")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_deep_research())
