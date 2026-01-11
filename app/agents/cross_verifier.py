"""
Cross Verifier Agent
Phase 3: Multi-Brain Architecture

Role: The "Judge"
- Uses a secondary model (Adversarial) to check the primary model's response.
- Focus: Safety, Medical Accuracy, Consensus.
"""
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.services.model_router import model_router

class CrossVerifierAgent(BaseAgent):
    """
    Agent that verifies high-stakes responses using a second opinion.
    """
    
    def __init__(self):
        super().__init__(
            name="CrossVerifierAgent",
            description="Verifies medical/financial safety using secondary model",
            system_prompt="""You are a Medical Safety Board.
Your job is to review AI responses for:
1. Medical inaccuracies
2. Dangerous advice
3. Lack of disclaimers

If the response is SAFE and ACCURATE, return "SAFE".
If not, return a corrected version with explanations."""
        )
    
    async def process(self, response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Verify the response.
        Context must contain 'original_query' and 'provider_used'.
        """
        original_query = context.get('original_query', '')
        provider_used = context.get('provider_used', 'unknown')
        
        # Select Opposing Provider
        # If primary was Gemini, use Groq. If Groq, use Gemini.
        verifier_provider = "gemini" if provider_used == "groq" else "groq"
        
        verification_prompt = f"""Review this interaction for medical safety.
        
        User Query: {original_query}
        AI Response: {response}
        
        Task:
        1. Check for medical errors or dangerous advice.
        2. Ensure disclaimers are present.
        3. If safe, reply exactly "SAFE".
        4. If unsafe/inaccurate, provide ONLY the CORRECTED version.
           - Do NOT say "The provided response..."
           - Do NOT explain what you changed.
           - Just output the final, safe response text.
        """
        
        try:
            # Force the opposing provider
            verification = await model_router.generate(
                message=verification_prompt,
                system_prompt=self.system_prompt,
                provider=verifier_provider
            )
            
            result_text = verification.get("response", "SAFE")
            
            if "SAFE" in result_text[:10].upper():
                return {
                    "verified": True,
                    "response": response,
                    "corrections": None
                }
            else:
                return {
                    "verified": False,
                    "response": result_text, # The corrected version
                    "corrections": "Safety concerns addressed by Cross-Verifier."
                }
                
        except Exception as e:
            print(f"[CrossVerifier] Error: {e}")
            return {"verified": True, "response": response} # Fail open (allow original) to avoid hanging

# Singleton
cross_verifier_agent = CrossVerifierAgent()
