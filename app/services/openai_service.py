import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("⚠️ OpenAI API Key missing in environment variables.")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        # Using the latest GPT-4o model which supports Structured Outputs (JSON) natively
        self.model = "gpt-4o-2024-08-06"

    async def generate_response(self, prompt: str, system_instruction: str = None) -> str:
        """
        Standard chat completion for complex queries.
        """
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        
        # User prompt
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ OpenAI API Error: {str(e)}")
            return f"I encountered an error processing your request with VEDA Advanced Intelligence. Error: {str(e)}"

    async def generate_json(self, prompt: str, system_instruction: str = "You are a helpful assistant that outputs JSON.") -> dict:
        """
        Forces JSON output. Ideal for Diet Plans, Workout Logs, etc.
        """
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3 # Lower temperature for structural stability
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except json.JSONDecodeError:
            print("❌ OpenAI Error: Output was not valid JSON.")
            return {"error": "Failed to parse JSON response"}
        except Exception as e:
            print(f"❌ OpenAI API Error: {str(e)}")
            return {"error": str(e)}

# Singleton instance
openai_service = OpenAIService()
