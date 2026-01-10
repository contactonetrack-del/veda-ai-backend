"""
Web Search Service
Real-time web search using Brave Search API + Tavily fallback
Phase 1: Perplexity-class Intelligence

API Quotas (AUTO-TRACKED):
- Brave Search: 2,000 requests/month (FREE)
- Tavily: 100 requests for basic (FREE)
- Groq: Unlimited (fallback when quotas exceeded)

Features:
- Automatic quota tracking with monthly reset
- Intelligent fallback chain: Brave → Tavily → Groq
- Persistent storage for quota counts
"""
import httpx
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from app.core.config import get_settings

settings = get_settings()

# Quota limits
MONTHLY_QUOTAS = {
    "brave": 2000,
    "tavily": 100
}

# File for persistent quota tracking
QUOTA_FILE = Path(__file__).parent.parent.parent / ".quota_usage.json"


class QuotaManager:
    """Tracks API usage and enforces monthly quotas"""
    
    def __init__(self):
        self.usage = self._load_usage()
    
    def _load_usage(self) -> Dict:
        """Load usage from persistent storage"""
        try:
            if QUOTA_FILE.exists():
                data = json.loads(QUOTA_FILE.read_text())
                # Check if it's a new month - reset if so
                if data.get("month") != datetime.now().strftime("%Y-%m"):
                    return self._create_new_month()
                return data
        except Exception as e:
            print(f"[QuotaManager] Load error: {e}")
        return self._create_new_month()
    
    def _create_new_month(self) -> Dict:
        """Create fresh usage tracking for new month"""
        data = {
            "month": datetime.now().strftime("%Y-%m"),
            "brave": 0,
            "tavily": 0,
            "groq_fallback": 0
        }
        self._save_usage(data)
        return data
    
    def _save_usage(self, data: Dict = None):
        """Persist usage to file"""
        try:
            QUOTA_FILE.write_text(json.dumps(data or self.usage, indent=2))
        except Exception as e:
            print(f"[QuotaManager] Save error: {e}")
    
    def can_use(self, service: str) -> bool:
        """Check if service has remaining quota"""
        limit = MONTHLY_QUOTAS.get(service, float('inf'))
        current = self.usage.get(service, 0)
        return current < limit
    
    def record_usage(self, service: str):
        """Record a usage increment"""
        self.usage[service] = self.usage.get(service, 0) + 1
        self._save_usage()
    
    def get_remaining(self, service: str) -> int:
        """Get remaining quota for a service"""
        limit = MONTHLY_QUOTAS.get(service, float('inf'))
        current = self.usage.get(service, 0)
        return max(0, limit - current)
    
    def get_status(self) -> Dict:
        """Get full quota status"""
        return {
            "month": self.usage.get("month"),
            "brave": {
                "used": self.usage.get("brave", 0),
                "limit": MONTHLY_QUOTAS["brave"],
                "remaining": self.get_remaining("brave"),
                "exceeded": not self.can_use("brave")
            },
            "tavily": {
                "used": self.usage.get("tavily", 0),
                "limit": MONTHLY_QUOTAS["tavily"],
                "remaining": self.get_remaining("tavily"),
                "exceeded": not self.can_use("tavily")
            },
            "groq_fallback_count": self.usage.get("groq_fallback", 0)
        }


class WebSearchService:
    """
    Multi-source web search with intelligent fallback.
    
    Priority Chain:
    1. Brave Search (privacy-focused, 2K/month free)
    2. Tavily (AI-optimized snippets, 100 free)
    3. Groq LLM (unlimited, knowledge-based fallback)
    """
    
    def __init__(self):
        self.brave_key = getattr(settings, 'BRAVE_API_KEY', '') or os.getenv("BRAVE_API_KEY", "")
        self.tavily_key = getattr(settings, 'TAVILY_API_KEY', '') or os.getenv("TAVILY_API_KEY", "")
        self.quota = QuotaManager()
        self._session_count = {"brave": 0, "tavily": 0, "groq": 0}
    
    @property
    def is_available(self) -> bool:
        """Check if any search option is available (always True with Groq fallback)"""
        return True  # Groq is always available as fallback
    
    @property
    def search_available(self) -> bool:
        """Check if actual web search APIs are available"""
        return bool(self.brave_key or self.tavily_key)
    
    async def search_brave(self, query: str, count: int = 5) -> List[Dict]:
        """Primary search using Brave Search"""
        if not self.brave_key:
            return []
        
        # Check quota
        if not self.quota.can_use("brave"):
            print(f"[WebSearch] Brave quota exceeded ({MONTHLY_QUOTAS['brave']}/month)")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers={
                        "Accept": "application/json",
                        "X-Subscription-Token": self.brave_key
                    },
                    params={"q": query, "count": min(count, 10)}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("web", {}).get("results", [])
                    self.quota.record_usage("brave")
                    self._session_count["brave"] += 1
                    
                    return [{
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "description": r.get("description", ""),
                        "source": "brave",
                        "favicon": r.get("favicon", "")
                    } for r in results[:count]]
                
                elif response.status_code == 429:
                    print("[WebSearch] Brave rate limit (429)")
                    return []
                    
        except httpx.TimeoutException:
            print("[WebSearch] Brave timeout")
        except Exception as e:
            print(f"[WebSearch] Brave error: {e}")
        
        return []
    
    async def search_tavily(self, query: str, count: int = 5) -> List[Dict]:
        """Fallback search using Tavily"""
        if not self.tavily_key:
            return []
        
        # Check quota
        if not self.quota.can_use("tavily"):
            print(f"[WebSearch] Tavily quota exceeded ({MONTHLY_QUOTAS['tavily']}/month)")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.tavily_key,
                        "query": query,
                        "max_results": min(count, 5),
                        "include_answer": True,
                        "search_depth": "basic"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.quota.record_usage("tavily")
                    self._session_count["tavily"] += 1
                    
                    results = []
                    
                    if data.get("answer"):
                        results.append({
                            "title": "AI Summary",
                            "url": "",
                            "description": data.get("answer"),
                            "source": "tavily_answer",
                            "is_ai_summary": True
                        })
                    
                    for r in data.get("results", []):
                        results.append({
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "description": r.get("content", ""),
                            "source": "tavily",
                            "score": r.get("score", 0)
                        })
                    
                    return results[:count]
                    
        except httpx.TimeoutException:
            print("[WebSearch] Tavily timeout")
        except Exception as e:
            print(f"[WebSearch] Tavily error: {e}")
        
        return []
    
    async def groq_knowledge_fallback(self, query: str) -> Dict:
        """
        Ultimate fallback: Use Groq's LLM for knowledge-based answers.
        Used when all search quotas are exceeded.
        """
        from app.services.groq_service import groq_service
        
        self.quota.record_usage("groq_fallback")
        self._session_count["groq"] += 1
        
        fallback_prompt = f"""The user asked: {query}

IMPORTANT: You don't have access to real-time web search right now. 
Answer based on your training knowledge. Be honest about limitations.

If the question requires very recent information:
- Acknowledge you may not have the latest data
- Provide what you know from your training
- Suggest the user verify with current sources

Provide a helpful, accurate response:"""

        try:
            response = await groq_service.generate_response(
                message=fallback_prompt,
                system_prompt="You are VEDA AI, a helpful wellness assistant. Answer based on your knowledge."
            )
            
            return {
                "results": [{
                    "title": "AI Knowledge Response",
                    "url": "",
                    "description": response,
                    "source": "groq_knowledge",
                    "is_fallback": True
                }],
                "source": "groq_knowledge",
                "count": 1,
                "success": True,
                "is_fallback": True,
                "fallback_reason": "search_quota_exceeded"
            }
        except Exception as e:
            print(f"[WebSearch] Groq fallback error: {e}")
            return {
                "results": [],
                "source": None,
                "count": 0,
                "success": False,
                "error": str(e)
            }
    
    async def smart_search(self, query: str, count: int = 5) -> Dict:
        """
        Intelligent search with automatic quota-aware fallback.
        
        Chain:
        1. Brave (if quota available)
        2. Tavily (if quota available)
        3. Groq knowledge (unlimited fallback)
        """
        results = []
        source = None
        is_fallback = False
        
        # Try Brave first (if quota available)
        if self.brave_key and self.quota.can_use("brave"):
            results = await self.search_brave(query, count)
            if results:
                source = "brave"
        
        # Try Tavily if Brave failed or quota exceeded
        if not results and self.tavily_key and self.quota.can_use("tavily"):
            results = await self.search_tavily(query, count)
            if results:
                source = "tavily"
        
        # Ultimate fallback to Groq knowledge
        if not results:
            print("[WebSearch] All search quotas exceeded, using Groq knowledge fallback")
            return await self.groq_knowledge_fallback(query)
        
        return {
            "results": results,
            "source": source,
            "count": len(results),
            "query": query,
            "success": len(results) > 0,
            "is_fallback": False
        }
    
    async def search_news(self, query: str, count: int = 5) -> Dict:
        """Search for news (Brave News cluster)"""
        if not self.brave_key or not self.quota.can_use("brave"):
            # Fallback to Groq for news queries
            return await self.groq_knowledge_fallback(f"latest news about {query}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.search.brave.com/res/v1/news/search",
                    headers={
                        "Accept": "application/json",
                        "X-Subscription-Token": self.brave_key
                    },
                    params={"q": query, "count": min(count, 10), "freshness": "pd"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    self.quota.record_usage("brave")
                    
                    return {
                        "results": [{
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "description": r.get("description", ""),
                            "source": "brave_news",
                            "published": r.get("age", ""),
                            "publisher": r.get("meta_url", {}).get("hostname", "")
                        } for r in results[:count]],
                        "source": "brave_news",
                        "count": len(results),
                        "success": True
                    }
                    
        except Exception as e:
            print(f"[WebSearch] News search error: {e}")
        
        return await self.groq_knowledge_fallback(f"latest news about {query}")
    
    def get_usage_stats(self) -> Dict:
        """Get comprehensive usage statistics"""
        return {
            **self.quota.get_status(),
            "session_counts": self._session_count,
            "search_configured": self.search_available,
            "fallback_available": True
        }


# Singleton instance
web_search = WebSearchService()

