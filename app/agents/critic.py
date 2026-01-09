"""
Critic Agent
Quality assurance agent that reviews responses before sending to user
"""
from typing import Dict, Any
from app.agents.base import BaseAgent


class CriticAgent(BaseAgent):
    """Reviews and validates responses before sending to user"""
    
    def __init__(self):
        super().__init__(
            name="Quality Reviewer",
            description="Reviews responses for accuracy and appropriateness",
            system_prompt="""You are a quality reviewer for VEDA AI health responses.

## Your Job:
Review the draft response and check for:

1. **Accuracy**: Is the information factually correct?
2. **Safety**: Does it avoid harmful medical/financial advice?
3. **Completeness**: Does it fully answer the user's question?
4. **Tone**: Is it warm, supportive, and culturally appropriate?
5. **Disclaimers**: For health/insurance topics, are proper disclaimers included?

## Response Format:
APPROVED: [yes/no]
ISSUES: [list any problems found]
IMPROVED: [if not approved, provide improved version]

## Automatic Approval Criteria:
- Greetings and general queries: Always approve
- Health advice with disclaimer: Approve
- Tool calculations with accurate results: Approve

## Rejection Criteria:
- Specific medical diagnoses
- Guaranteed claims about health outcomes
- Specific financial product recommendations without disclaimer
- Culturally insensitive content"""
        )
    
    async def process(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Review a draft response"""
        
        draft_response = context.get("draft_response", "")
        intent = context.get("intent", "general")
        
        # Fast-track approvals for low-risk content
        if intent == "general":
            return {
                "agent": self.name,
                "approved": True,
                "final_response": draft_response,
                "review_notes": "General query - auto-approved"
            }
        
        # For tool results, approve if successful
        if intent == "tool" and context.get("tool_success", False):
            return {
                "agent": self.name,
                "approved": True,
                "final_response": draft_response,
                "review_notes": "Tool calculation - auto-approved"
            }
        
        # For wellness and protection, do a quick review
        review_prompt = f"""User asked: {user_message}

Draft response:
{draft_response}

Review this response for accuracy, safety, and appropriateness."""
        
        review_result = await self.generate(review_prompt)
        
        # Parse review result
        approved = "APPROVED: yes" in review_result.lower() or "approved: yes" in review_result.lower()
        
        if approved:
            return {
                "agent": self.name,
                "approved": True,
                "final_response": draft_response,
                "review_notes": "Passed quality review"
            }
        else:
            # Try to extract improved version
            if "IMPROVED:" in review_result:
                improved = review_result.split("IMPROVED:")[-1].strip()
                return {
                    "agent": self.name,
                    "approved": True,
                    "final_response": improved,
                    "review_notes": "Improved by reviewer"
                }
            else:
                # Add standard disclaimer and approve
                final = draft_response + "\n\n_Disclaimer: This is general guidance. Please consult a qualified professional for personalized advice._"
                return {
                    "agent": self.name,
                    "approved": True,
                    "final_response": final,
                    "review_notes": "Added disclaimer"
                }


# Singleton instance
critic_agent = CriticAgent()
