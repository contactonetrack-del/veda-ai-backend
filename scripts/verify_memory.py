import requests
import asyncio
import json

BASE_URL = "http://localhost:8000/api/v1"
USER_ID = "test_user_memory"

def colored_print(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def verify_memory_api():
    print(f"--- Verifying Memory API on {BASE_URL} ---")
    
    # 1. Add some dummy memory (via Orchestrator or similar... wait, no direct add endpoint exposed yet?)
    # The memory is added automatically when chatting. 
    # But I can use knowledge base add? No, vector memory is for chat history.
    # So I will just Try to GET. If empty, that's fine, but 200 OK is needed.
    
    print("\n1. Testing GET /memory")
    try:
        response = requests.get(f"{BASE_URL}/memory/?user_id={USER_ID}")
        if response.status_code == 200:
            colored_print(f"[OK] GET /memory returned {len(response.json())} items", "green")
        else:
            colored_print(f"[FAIL] GET /memory failed: {response.text}", "red")
    except Exception as e:
        colored_print(f"[ERROR] Could not connect: {e}", "red")
        return

    # 2. Test Delete (if any exist)
    # response = requests.delete(...)
    
    print("\n2. Testing DELETE /memory (Clear All)")
    try:
        response = requests.delete(f"{BASE_URL}/memory/?user_id={USER_ID}")
        if response.status_code == 200:
             colored_print("[OK] DELETE /memory (Clear) successful", "green")
        else:
             colored_print(f"[FAIL] Clear failed: {response.text}", "red")
    except Exception as e:
        colored_print(f"[ERROR] Delete failed: {e}", "red")

if __name__ == "__main__":
    verify_memory_api()
