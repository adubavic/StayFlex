"""
Rate limiting middleware for FastAPI
"""
from fastapi import Request, HTTPException, status
from functools import wraps
import time
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.blocked: Dict[str, float] = {}
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Check if request is allowed under rate limit.
        Returns (allowed, retry_after_seconds)
        """
        now = time.time()
        
        # Check if IP is blocked
        if key in self.blocked:
            block_expires = self.blocked[key]
            if now < block_expires:
                retry_after = int(block_expires - now)
                return False, retry_after
            else:
                del self.blocked[key]
        
        # Initialize request list for key
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window_seconds
        ]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= max_requests:
            retry_after = int(self.requests[key][0] + window_seconds - now)
            # Block for 5 minutes on rate limit hit
            self.blocked[key] = now + 300
            return False, retry_after
        
        # Record this request
        self.requests[key].append(now)
        return True, 0
    
    def cleanup(self):
        """Clean up old entries"""
        now = time.time()
        # Clean requests
        for key in list(self.requests.keys()):
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < 3600  # Keep last hour
            ]
            if not self.requests[key]:
                del self.requests[key]
        # Clean blocked
        for key in list(self.blocked.keys()):
            if now >= self.blocked[key]:
                del self.blocked[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 5, window_seconds: int = 60):
    """
    Rate limiting decorator for FastAPI endpoints.
    
    Args:
        max_requests: Maximum number of requests allowed in the window
        window_seconds: Time window in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request in args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get('request')
            
            if request:
                # Use IP + path as key
                client_ip = request.client.host if request.client else "unknown"
                key = f"{client_ip}:{request.url.path}"
                
                allowed, retry_after = rate_limiter.is_allowed(key, max_requests, window_seconds)
                
                if not allowed:
                    logger.warning(f"Rate limit exceeded for {key}")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                        headers={
                            "Retry-After": str(retry_after),
                            "X-RateLimit-Limit": str(max_requests),
                            "X-RateLimit-Window": str(window_seconds)
                        }
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def auth_rate_limit(max_requests: int = 5, window_seconds: int = 300):
    """
    Stricter rate limiting for authentication endpoints.
    Default: 5 requests per 5 minutes.
    """
    return rate_limit(max_requests=max_requests, window_seconds=window_seconds)
