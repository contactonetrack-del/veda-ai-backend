"""
Router Agent
Classifies user intent and routes to appropriate specialist agent
"""
from typing import Dict, Any
from app.agents.base import BaseAgent


class RouterAgent(BaseAgent):
    """Routes user queries to the appropriate specialist agent"""
    
    def __init__(self):
        super().__init__(
            name="Router",
            description="Classifies user intent and routes to specialists",
            system_prompt="""You are an intent classifier for VEDA AI, a wellness and intelligence assistant.

Your job is to classify user messages into ONE of these categories:
- "wellness": Nutrition, diet, fitness, exercise, yoga, meditation, Ayurveda, weight management
- "protection": Health insurance, medical coverage, claims, policies, family health plans (frame as "health protection", not finance)
- "tool": User explicitly wants a calculation (calories, BMI, premium estimate)
- "search": Queries requiring REAL-TIME information (news, updates)
- "research": Requests for DEEP analysis, reports, investigations, or complex topics requiring synthesis
- "analysis": Requests requiring math, statistics, data processing, or pattern finding
- "general": Greetings, about VEDA, unclear queries, casual conversation

IMPORTANT: Use "analysis" for:
- "Analyze this data..."
- "Find trends in..."
- "Calculate correlation between..."
- "Predict my..."
- Mathematical or statistical questions

IMPORTANT: Use "research" for:
- "Write a report on..."
- "Deep dive into..."
- "Investigate..."
- "Comprehensive analysis of..."
- "Research X vs Y"
- Current events or live information
- "What is happening with..."
- Questions requiring up-to-date data
- Topics where information changes frequently

Respond with ONLY the category name, nothing else.

Examples:
"How many calories in dosa?" → wellness
"Best health insurance for family" → protection
"Calculate my BMI" → tool
"Hello, who are you?" → general
"What's a good workout for back pain?" → wellness
"Explain claim process" → protection
"I want to lose 5kg" → wellness
"Premium for 10 lakh cover?" → tool
"What's the latest research on intermittent fasting?" → search
"Current news about COVID vaccine" → search
"Tell me about recent health trends" → search
"What's happening in AI today?" → search"""
        )
    
    async def process(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Classify intent and return routing decision"""
        
        # Use Gemini to classify
        classification = await self.generate(user_message)
        
        # Clean the response
        intent = classification.strip().lower()
        
        # Validate classification
        valid_intents = ["wellness", "protection", "tool", "search", "general", "research", "analysis"]
        if intent not in valid_intents:
            # Default to general if unclear
            intent = "general"
        
        return {
            "intent": intent,
            "original_message": user_message,
            "route_to": self._get_agent_for_intent(intent)
        }
    
    def _get_agent_for_intent(self, intent: str) -> str:
        """Map intent to agent name"""
        mapping = {
            "wellness": "WellnessAgent",
            "protection": "ProtectionAgent",
            "tool": "ToolAgent",
            "search": "SearchAgent",
            "research": "DeepResearchAgent",
            "analysis": "DataAnalystAgent",
            "general": "GeneralAgent"
        }
        return mapping.get(intent, "GeneralAgent")


# Singleton instance
router_agent = RouterAgent()
