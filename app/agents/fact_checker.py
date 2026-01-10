"""
Fact-Checker Agent
Phase 2: Intelligence Layer

Verifies AI-generated responses by cross-checking claims against web search results.
Reduces hallucinations and improves trustworthiness.
"""
from typing import Dict, List, Optional
from app.agents.base import BaseAgent
from app.services.groq_service import groq_service
from app.services.web_search import web_search
import re


class FactCheckerAgent(BaseAgent):
    """
    Agent that verifies factual claims in AI responses.
    
    Process:
    1. Extract verifiable claims from response
    2. Search for evidence for each claim
    3. Assign confidence scores
    4. Rewrite if low confidence detected
    """
    
    def __init__(self):
        super().__init__(
            name="FactCheckerAgent",
            description="Verifies factual accuracy of AI responses",
            system_prompt="You are a fact-checking assistant that verifies claims against evidence."
        )
    
    async def process(self, message: str, context: Dict = None) -> Dict:
        """
        Verify a response for factual accuracy.
        
        Args:
            message: The AI response to verify
            context: Must contain 'original_query' and optionally 'sources'
            
        Returns:
            Dict with verified response and confidence score
        """
        original_query = context.get('original_query', '') if context else ''
        existing_sources = context.get('sources', []) if context else []
        
        # Step 1: Extract claims
        claims = await self._extract_claims(message)
        
        if not claims:
            # No verifiable claims, return as-is with high confidence
            return {
                "verified_response": message,
                "confidence": 0.95,
                "verified": True,
                "claims_checked": 0,
                "sources": existing_sources
            }
        
        # Step 2: Verify each claim
        verification_results = []
        all_sources = list(existing_sources)
        
        for claim in claims[:3]:  # Limit to top 3 claims to save quota
            result = await self._verify_claim(claim, original_query)
            verification_results.append(result)
            if result.get('sources'):
                all_sources.extend(result['sources'])
        
        # Step 3: Calculate overall confidence
        confidence = self._calculate_confidence(verification_results)
        
        # Step 4: Rewrite if needed
        if confidence < 0.6:
            verified_response = await self._rewrite_with_corrections(
                message, 
                original_query,
                verification_results
            )
        else:
            verified_response = message
        
        return {
            "verified_response": verified_response,
            "confidence": confidence,
            "verified": confidence >= 0.6,
            "claims_checked": len(claims),
            "verification_details": verification_results,
            "sources": all_sources
        }
    
    async def _extract_claims(self, response: str) -> List[str]:
        """Extract verifiable factual claims from response"""
        prompt = f"""Extract ONLY the verifiable factual claims from this response.
Ignore opinions, recommendations, or general statements.

Response: {response}

List each claim on a new line. Maximum 5 claims.
Claims:"""

        try:
            result = await groq_service.generate_response(
                message=prompt,
                system_prompt="You extract factual claims. Be concise."
            )
            
            # Parse claims (one per line)
            claims = [c.strip() for c in result.split('\n') if c.strip() and not c.strip().startswith('#')]
            return claims[:5]
        except Exception as e:
            print(f"[FactChecker] Claim extraction error: {e}")
            return []
    
    async def _verify_claim(self, claim: str, context: str) -> Dict:
        """Verify a single claim using web search"""
        # Create search query
        search_query = f"{claim} {context}"[:100]
        
        try:
            # Search for evidence
            search_result = await web_search.smart_search(search_query, count=3)
            
            if not search_result.get('success'):
                return {
                    "claim": claim,
                    "verified": False,
                    "confidence": 0.3,
                    "evidence": "No search results found"
                }
            
            # Analyze evidence
            sources = search_result.get('results', [])
            evidence_text = "\n".join([
                f"- {s.get('title', '')}: {s.get('description', '')[:200]}"
                for s in sources[:3]
            ])
            
            # Ask LLM to verify
            verification_prompt = f"""Claim: {claim}

Evidence from web search:
{evidence_text}

Does the evidence support this claim? Answer with:
- SUPPORTED: Evidence clearly supports the claim
- CONTRADICTED: Evidence contradicts the claim
- UNCLEAR: Not enough evidence or mixed results

Answer:"""

            verification = await groq_service.generate_response(
                message=verification_prompt,
                system_prompt="You verify claims against evidence. Be strict."
            )
            
            # Parse result
            verification_lower = verification.lower()
            if 'supported' in verification_lower:
                confidence = 0.9
                verified = True
            elif 'contradicted' in verification_lower:
                confidence = 0.1
                verified = False
            else:
                confidence = 0.5
                verified = False
            
            return {
                "claim": claim,
                "verified": verified,
                "confidence": confidence,
                "evidence": evidence_text[:300],
                "sources": sources
            }
            
        except Exception as e:
            print(f"[FactChecker] Verification error: {e}")
            return {
                "claim": claim,
                "verified": False,
                "confidence": 0.3,
                "evidence": f"Error: {str(e)}"
            }
    
    def _calculate_confidence(self, verification_results: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not verification_results:
            return 0.8  # Default if no claims to verify
        
        confidences = [r.get('confidence', 0.5) for r in verification_results]
        return sum(confidences) / len(confidences)
    
    async def _rewrite_with_corrections(
        self, 
        original: str, 
        query: str,
        verifications: List[Dict]
    ) -> str:
        """Rewrite response with corrections based on verification"""
        
        # Build correction context
        corrections = []
        for v in verifications:
            if not v.get('verified'):
                corrections.append(f"- Claim '{v['claim']}' is not well-supported. Evidence: {v.get('evidence', 'None')}")
        
        correction_text = "\n".join(corrections) if corrections else "Some claims need revision."
        
        rewrite_prompt = f"""Original query: {query}

Original response: {original}

Issues found:
{correction_text}

Rewrite the response to be more accurate. Remove or correct unsupported claims. Keep the helpful tone.

Revised response:"""

        try:
            revised = await groq_service.generate_response(
                message=rewrite_prompt,
                system_prompt="You are a fact-checker. Rewrite responses to be accurate and honest about limitations."
            )
            return revised
        except Exception as e:
            print(f"[FactChecker] Rewrite error: {e}")
            return original + "\n\n⚠️ Note: Some claims in this response could not be verified."


# Singleton instance
fact_checker = FactCheckerAgent()
