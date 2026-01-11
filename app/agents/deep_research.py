"""
Deep Research Agent
Phase 3: Deep Intelligence

Workflow:
1. Analyze Query -> Create Research Plan (Sub-questions)
2. Iterate through Sub-questions:
   - Search Web
   - Extract Information
   - Refine Plan (if needed)
3. Synthesize Comprehensive Report
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.web_search import web_search
from app.services.groq_service import groq_service

class DeepResearchAgent(BaseAgent):
    """
    Agent that performs multi-step, deep research.
    """
    
    def __init__(self):
        super().__init__(
            name="DeepResearchAgent",
            description="Performs deep, recursive research on complex topics",
            system_prompt="""You are VEDA SAGE (Scientific Analysis & Global Evaluation), a PhD-level Research Scientist.
Your process is rigorous, skeptical, and exhaustive.
You do NOT settle for surface-level answers. You verify claims, seek contradictions, and synthesize cross-domain knowledge.
Your reports are "Harvard Business Review" quality: dense with insight, clear in structure, and backed by data."""
        )
    
    async def process(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute deep research workflow.
        """
        # Step 1: Create Research Plan
        plan = await self._create_plan(user_message)
        
        # Step 2: Execute Research Loop
        gathered_info = []
        sources = []
        
        for step in plan[:4]: # Expanded to 4 steps for deeper analysis
            query = step.get('query')
            if not query: continue
            
            # Search
            search_result = await web_search.smart_search(query)
            if search_result.get('results'):
                sources.extend(search_result['results'][:2])
                
                # Extract insights
                insights = await self._extract_insights(query, search_result['results'])
                gathered_info.append(f"## {step.get('focus')}\n{insights}")
        
        # Step 3: Synthesize Final Report
        report = await self._generate_report(user_message, gathered_info)
        
        return {
            "response": report,
            "success": True,
            "agent": "DeepResearchAgent",
            "sources": self._format_sources_unique(sources),
            "intent": "deep_research"
        }

    async def _create_plan(self, query: str) -> List[Dict]:
        """Generate search queries and focus areas"""
        prompt = f"""Create a rigorous research plan for: "{query}"

        Identify 4 distinct critical angles (e.g., Scientific Mechanism, Market Data, Legal/Safety, Future Outlook).
        
        Return exactly 4 search steps in this format (ONE PER LINE):
        1. QUERY: <precise_search_query> | FOCUS: <specific_data_to_extract>
        2. QUERY: <precise_search_query> | FOCUS: <specific_data_to_extract>
        3. QUERY: <precise_search_query> | FOCUS: <specific_data_to_extract>
        4. QUERY: <precise_search_query> | FOCUS: <specific_data_to_extract>"""
        
        response = await groq_service.generate_response(prompt, system_prompt="You are a strategic researcher.")
        
        # Parse logic (simplified for MVP)
        steps = []
        for line in response.split('\n'):
            if "QUERY:" in line and "FOCUS:" in line:
                parts = line.split('|')
                q = parts[0].split('QUERY:')[1].strip()
                f = parts[1].split('FOCUS:')[1].strip()
                steps.append({"query": q, "focus": f})
        return steps

    async def _extract_insights(self, query: str, results: List[Dict]) -> str:
        """Summarize search results for a specific step"""
        context = "\n".join([f"- {r['title']}: {r['description']}" for r in results])
        prompt = f"""Analyze these search results for "{query}".
        Context:
        {context}
        
        Goal: Extract high-value facts, statistics, and scientific consensus.
        Ignore marketing fluff. Focus on hard data and contradictions.
        Write a dense paragraph."""
        return await groq_service.generate_response(prompt, fast=True)

    async def _generate_report(self, query: str, info: List[str]) -> str:
        """Write the final report"""
        context = "\n\n".join(info)
        prompt = f"""Synthesize a "Super-Intelligence" Report on: "{query}"
        
        INPUT DATA:
        {context}
        
        REQUIREMENTS:
        1. **Executive Synthesis**: The "Bottom Line" up front (BLUF).
        2. **Deep Dive**: Analysis of the 4 dimensions researched.
        3. **Consensus & Contradictions**: What is proven vs. what is debated?
        4. **Actionable Advice**: If applicable, what should the user DO?
        
        TONE: Authoritative, Nuanced, and Data-Driven.
        FORMAT: Professional Markdown."""
        return await groq_service.generate_response(prompt, system_prompt=self.system_prompt)

    def _format_sources_unique(self, sources: List[Dict]) -> List[Dict]:
        """Deduplicate sources based on URL"""
        seen = set()
        unique = []
        for s in sources:
            if s['url'] not in seen:
                seen.add(s['url'])
                formatted = {
                    "title": s.get("title", "Source"),
                    "url": s.get("url"),
                    "favicon": s.get("favicon", ""),
                    "source_type": s.get("source", "web")
                }
                unique.append(formatted)
        return unique

# Singleton
deep_research_agent = DeepResearchAgent()
