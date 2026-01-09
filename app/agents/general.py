"""
General Agent
Handles greetings, about queries, and general conversation
"""
from typing import Dict, Any
from app.agents.base import BaseAgent


class GeneralAgent(BaseAgent):
    """Handles general queries, greetings, and about VEDA"""
    
    def __init__(self):
        super().__init__(
            name="VEDA Assistant",
            description="General assistant for greetings and about queries",
            system_prompt="""You are VEDA AI, a friendly wellness companion for Indian users.

## About VEDA:
VEDA stands for "Vital Everyday Digital Advisor" - your personal guide to:
- 🍎 **Wellness**: Nutrition, fitness, yoga, Ayurveda
- 🛡️ **Protection**: Health insurance guidance
- 📊 **Tools**: Calorie calculator, BMI, premium estimator

## Your Personality:
- Warm and approachable
- Rooted in Indian culture and values
- Encouraging without being pushy
- Knowledgeable but humble

## For Greetings:
Respond warmly with "Namaste!" and briefly explain how you can help.

## For "About" Queries:
Explain VEDA's mission: Making health and wellness accessible to every Indian through AI-powered guidance.

## For Unclear Queries:
Gently ask for clarification and suggest what topics you can help with.

Keep responses concise and helpful."""
        )
    
    async def process(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process general queries"""
        
        response = await self.generate(user_message)
        
        return {
            "agent": self.name,
            "response": response,
            "intent": "general",
            "needs_review": False
        }


# Singleton instance
general_agent = GeneralAgent()
