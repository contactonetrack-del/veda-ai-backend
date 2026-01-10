"""
In-memory rate limiter for zero-cost API protection.
Supports up to ~1000 concurrent users without Redis.
"""

from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List
import threading


class InMemoryRateLimiter:
    """
    Thread-safe in-memory rate limiter.
    For production scale (>1000 users), upgrade to Redis.
    """
    
    def __init__(self):
        self._requests: Dict[str, List[datetime]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def allow(
        self, 
        key: str, 
        limit: int = 5, 
        window_seconds: int = 3600
    ) -> bool:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Unique identifier (e.g., "vision:user_ip")
            limit: Max requests allowed in window
            window_seconds: Time window in seconds (default: 1 hour)
        
        Returns:
            True if allowed, False if rate limited
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        with self._lock:
            # Clean old requests outside window
            self._requests[key] = [
                t for t in self._requests[key] 
                if t > window_start
            ]
            
            # Check if under limit
            if len(self._requests[key]) >= limit:
                return False
            
            # Record this request
            self._requests[key].append(now)
            return True
    
    def get_remaining(self, key: str, limit: int = 5) -> int:
        """Get remaining requests for this key."""
        with self._lock:
            return max(0, limit - len(self._requests.get(key, [])))
    
    def reset(self, key: str):
        """Reset rate limit for a key (for testing)."""
        with self._lock:
            self._requests.pop(key, None)


# Global instance
rate_limiter = InMemoryRateLimiter()
