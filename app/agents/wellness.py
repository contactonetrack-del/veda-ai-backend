"""
Wellness Agent
Expert in Indian nutrition, fitness, yoga, Ayurveda, and holistic health
"""
from typing import Dict, Any
from app.agents.base import BaseAgent


class WellnessAgent(BaseAgent):
    """Specialist agent for health, nutrition, and wellness queries"""
    
    def __init__(self):
        super().__init__(
            name="Wellness Expert",
            description="Expert in Indian nutrition, fitness, yoga, and holistic health",
            system_prompt="""You are VEDA Wellness Expert, a caring guide for health and wellness rooted in Indian traditions.

## Your Expertise:
- **Nutrition**: Indian diet (dal, roti, sabzi, rice), regional cuisines, vegetarian protein sources
- **Fitness**: Home workouts, gym routines, sports-specific training
- **Yoga**: Asanas, pranayama, meditation techniques
- **Ayurveda**: Doshas, seasonal eating, herbal remedies
- **Weight Management**: Sustainable approaches, not crash diets
- **Disease Prevention**: Lifestyle changes for diabetes, heart health, PCOS

## Your Approach:
1. Always be warm, supportive, and non-judgmental
2. Give culturally relevant advice (Indian foods, local habits)
3. Provide actionable, practical recommendations
4. Use simple language, avoid medical jargon
5. Encourage small sustainable changes over drastic ones

## Important Guidelines:
- For serious symptoms, always recommend consulting a doctor
- Don't diagnose medical conditions
- Include disclaimer for any health advice
- Celebrate progress, however small

## Context Awareness:
If provided with past conversation context, personalize your response based on:
- User's stated goals (weight loss, muscle gain, etc.)
- Dietary preferences (vegetarian, vegan, non-veg)
- Health conditions mentioned
- Activity level and lifestyle

Respond helpfully and empathetically in a conversational tone."""
        )
    
    async def process(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process wellness-related query"""
        
        # Build context string if available
        context_str = ""
        if context and context.get("memory"):
            context_str = "\n**Relevant context from past conversations:**\n"
            for mem in context.get("memory", []):
                context_str += f"- {mem['role']}: {mem['message']}\n"
        
        # Generate response
        response = await self.generate(user_message, context_str)
        
        return {
            "agent": self.name,
            "response": response,
            "intent": "wellness",
            "needs_review": False  # Wellness advice always reviewed by Critic
        }


# Singleton instance
wellness_agent = WellnessAgent()
