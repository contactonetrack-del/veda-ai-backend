import requests
import os
import json

api_key = "b780baa17d694a82aed23e1f6d44c840.2DyM8EvDH_iNFqBi8wb9e35I"
url = "https://ollama.com/api/tags"

try:
    response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
    response.raise_for_status()
    models = response.json().get("models", [])
    print(f"Found {len(models)} models available in Cloud:")
    for m in models:
        print(f"- {m['name']}")
except Exception as e:
    print(f"Error: {e}")
