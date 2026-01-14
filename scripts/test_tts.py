
import requests
import os
import sys

# Backend URL (verify port matches your local running instance, usually 8000)
BASE_URL = "http://localhost:8000/api/v1"

def test_synthesize():
    url = f"{BASE_URL}/voice/synthesize"
    
    # Payload
    params = {
        "text": "Namaste! This is a test of the VEDA AI voice engine.",
        "language": "hi",
        "description": "A warm greeting"
    }
    
    print(f"Testing TTS synthesis at {url}...")
    try:
        response = requests.post(url, params=params, stream=True)
        
        if response.status_code == 200:
            print("[OK] Success! TTS Request accepted.")
            
            filename = "test_output.wav"
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"[OK] Audio saved to {filename}")
            
            size = os.path.getsize(filename)
            print(f"File size: {size} bytes")
            if size > 1000:
                print("[OK] File size looks valid (>1KB).")
            else:
                print("[ERROR] File size too small (likely error or empty).")
                
        else:
            print(f"[ERROR] Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("Hint: Is the backend running? (uvicorn app.main:app)")

if __name__ == "__main__":
    test_synthesize()
