"""
Search Agent
Real-time web search with LLM synthesis
Phase 1: Perplexity-class Intelligence

Handles queries that require current/real-time information:
- Latest news and research
- Current events
- Live data queries
"""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.web_search import web_search
from app.services.groq_service import groq_service


class SearchAgent(BaseAgent):
    """
    Handles queries requiring real-time web information.
    
    Flow:
    1. Perform web search via Brave/Tavily
    2. Synthesize results using Groq LLM
    3. Return response with citations
    """
    
    def __init__(self):
        super().__init__(
            name="SearchAgent",
            description="Web search and research synthesis",
            system_prompt="""You are VEDA AI's research assistant with access to real-time web information.

Your task is to synthesize web search results into clear, accurate, well-cited answers.

GUIDELINES:
1. **Cite sources** using [1], [2], etc. format
2. **Be objective** - Present facts, not opinions
3. **Highlight key findings** with bullet points
4. **Note conflicting information** if sources disagree
5. **Keep responses concise** but comprehensive
6. **Use headers** for long responses

FORMAT:
- Start with a brief summary (2-3 sentences)
- Use bullet points for key facts
- End with sources in format: [1] Source Title

IMPORTANT:
- If asked about health/medical topics, remind users to consult professionals
- Clearly indicate when information may be outdated
- Acknowledge if search results are limited"""
        )
    
    async def process(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Search web and synthesize results with citations.
        
        Args:
            user_message: The search query
            context: Additional context (memory, user_id, etc.)
            
        Returns:
            Dict with response, sources, and metadata
        """
        context = context or {}
        
        # Step 1: Check if web search is available
        if not web_search.is_available:
            return {
                "response": "I apologize, but web search is currently unavailable. Please try again later.",
                "success": False,
                "sources": [],
                "agent": "SearchAgent"
            }
        
        # Step 2: Determine if we need news or general web search
        is_news_query = self._is_news_query(user_message)
        
        # Step 3: Perform search
        if is_news_query:
            search_results = await web_search.search_news(user_message)
        else:
            search_results = await web_search.smart_search(user_message)
        
        results = search_results.get("results", [])
        
        # Step 4: Handle no results
        if not results:
            return {
                "response": "I couldn't find relevant information for your query. Please try rephrasing or make the query more specific.",
                "success": False,
                "sources": [],
                "search_query": user_message,
                "agent": "SearchAgent"
            }
        
        # Step 5: Format results for LLM synthesis
        sources_text = self._format_sources_for_llm(results)
        
        # Step 6: Synthesize with Groq (fast and free)
        synthesis_prompt = f"""Based on these search results, provide a comprehensive answer to the user's query.

USER QUERY: {user_message}

SEARCH RESULTS:
{sources_text}

INSTRUCTIONS:
1. Synthesize the information into a clear, helpful response
2. Cite sources using [1], [2], etc.
3. If information is conflicting, note both perspectives
4. Be concise but complete
5. Use markdown formatting for readability

Provide your response:"""

        try:
            response = await groq_service.generate_response(
                message=synthesis_prompt,
                system_prompt=self.system_prompt
            )
        except Exception as e:
            print(f"[SearchAgent] LLM synthesis error: {e}")
            # Fallback: Return raw search results if LLM fails
            response = self._format_fallback_response(results)
        
        # Step 7: Format sources for frontend
        sources = self._format_sources_for_response(results)
        
        return {
            "response": response,
            "success": True,
            "sources": sources,
            "search_query": search_results.get("query"),
            "search_source": search_results.get("source"),
            "result_count": len(results),
            "agent": "SearchAgent"
        }
    
    def _is_news_query(self, query: str) -> bool:
        """Detect if query is asking for news/current events"""
        news_indicators = [
            "news", "latest", "today", "yesterday", "recent",
            "breaking", "current", "update", "happening",
            "this week", "this month"
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in news_indicators)
    
    def _format_sources_for_llm(self, results: List[Dict]) -> str:
        """Format search results for LLM context"""
        formatted = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "Untitled")
            description = r.get("description", "")[:500]  # Limit description length
            url = r.get("url", "")
            
            formatted.append(f"[{i}] {title}\n{description}\nSource: {url}\n")
        
        return "\n".join(formatted)
    
    def _format_sources_for_response(self, results: List[Dict]) -> List[Dict]:
        """Format sources for frontend display"""
        sources = []
        for r in results:
            if r.get("url"):  # Only include sources with URLs
                sources.append({
                    "title": r.get("title", "Source"),
                    "url": r.get("url"),
                    "favicon": r.get("favicon", ""),
                    "source_type": r.get("source", "web")
                })
        return sources
    
    def _format_fallback_response(self, results: List[Dict]) -> str:
        """Create response if LLM synthesis fails"""
        lines = ["Here's what I found:\n"]
        for i, r in enumerate(results[:5], 1):
            title = r.get("title", "Result")
            desc = r.get("description", "")[:200]
            lines.append(f"**[{i}] {title}**\n{desc}\n")
        return "\n".join(lines)


# Singleton instance
search_agent = SearchAgent()
