
import asyncio
import os
import sys

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.web_search import web_search

async def test_search():
    print("[TEST] Testing Web Search Service...")
    
    # Check availability
    print(f"Available: {web_search.is_available}")
    print(f"Brave Key: {'[OK] Configured' if web_search.brave_key else '[MISSING]'}")
    print(f"Tavily Key: {'[OK] Configured' if web_search.tavily_key else '[MISSING]'}")
    
    # Test 1: News Search
    query = "latest advancements in AI 2025"
    print(f"\n[TEST] Testing News Search for: '{query}'...")
    try:
        results = await web_search.search_news(query)
        if results.get("success"):
            print(f"[OK] Found {results.get('count')} news items from {results.get('source')}")
            for r in results.get("results", [])[:2]:
                print(f"  - {r['title']} ({r['published']})")
        else:
            print(f"[FAIL] Search failed: {results}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

    # Test 2: General Search
    query = "price of iPhone 16 Pro Max in India"
    print(f"\n[TEST] Testing Smart Search for: '{query}'...")
    try:
        results = await web_search.smart_search(query)
        if results.get("success"):
            print(f"[OK] Found {results.get('count')} results from {results.get('source')}")
            for r in results.get("results", [])[:2]:
                print(f"  - {r['title']}")
        else:
            print(f"[FAIL] Search failed: {results}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
