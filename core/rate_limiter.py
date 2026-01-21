"""Rate limiting utilities for API calls.

Provides rate limiting for external API calls to avoid hitting rate limits
and to manage costs effectively.

Usage:
    from core.rate_limiter import RateLimiter, get_rate_limiter

    # Get rate limiter for a specific API
    limiter = get_rate_limiter("anthropic")

    # Use as decorator
    @limiter.limit
    async def call_api():
        ...

    # Or use directly
    async with limiter:
        await call_api()
"""

import asyncio
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from functools import wraps
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int = 60
    requests_per_day: int = 10000
    tokens_per_minute: int = 100000  # For LLM APIs
    concurrent_requests: int = 10
    retry_after_seconds: int = 60


# Default configurations per API
DEFAULT_CONFIGS = {
    "anthropic": RateLimitConfig(
        requests_per_minute=50,  # Claude API tier-1 limit
        requests_per_day=5000,
        tokens_per_minute=40000,
        concurrent_requests=5,
    ),
    "gemini": RateLimitConfig(
        requests_per_minute=60,  # Gemini API free tier
        requests_per_day=1500,
        tokens_per_minute=32000,
        concurrent_requests=10,
    ),
    "proxycurl": RateLimitConfig(
        requests_per_minute=30,  # Proxycurl rate limit
        requests_per_day=300,
        concurrent_requests=3,
    ),
    "airtable": RateLimitConfig(
        requests_per_minute=5,  # Airtable is 5 req/sec per base
        concurrent_requests=5,
    ),
    "default": RateLimitConfig(),
}


class RateLimiter:
    """Rate limiter with sliding window and concurrent request limiting.

    Features:
    - Sliding window rate limiting (requests per minute)
    - Daily request quota tracking
    - Concurrent request limiting
    - Automatic retry-after handling
    - Token-based limiting for LLM APIs
    """

    def __init__(
        self,
        name: str,
        config: Optional[RateLimitConfig] = None,
    ):
        """Initialize rate limiter.

        Args:
            name: Name of the API (for logging)
            config: Rate limit configuration. Uses defaults if not provided.
        """
        self.name = name
        self.config = config or DEFAULT_CONFIGS.get(name, DEFAULT_CONFIGS["default"])

        # Sliding window for requests per minute
        self._minute_window: deque[float] = deque()

        # Daily counter
        self._day_start: float = time.time()
        self._day_count: int = 0

        # Token tracking (for LLM APIs)
        self._token_window: deque[tuple[float, int]] = deque()

        # Concurrent request semaphore
        self._semaphore = asyncio.Semaphore(self.config.concurrent_requests)

        # Lock for thread safety
        self._lock = asyncio.Lock()

        logger.info(
            "rate_limiter_initialized",
            name=name,
            rpm=self.config.requests_per_minute,
            rpd=self.config.requests_per_day,
            concurrent=self.config.concurrent_requests,
        )

    async def acquire(self, tokens: int = 0) -> None:
        """Acquire permission to make a request.

        Blocks if rate limit would be exceeded.

        Args:
            tokens: Number of tokens this request will use (for LLM APIs)
        """
        async with self._lock:
            now = time.time()

            # Clean old entries from minute window
            while self._minute_window and now - self._minute_window[0] > 60:
                self._minute_window.popleft()

            # Check minute rate limit
            if len(self._minute_window) >= self.config.requests_per_minute:
                wait_time = 60 - (now - self._minute_window[0])
                if wait_time > 0:
                    logger.warning(
                        "rate_limit_minute_exceeded",
                        name=self.name,
                        waiting_seconds=round(wait_time, 2),
                    )
                    await asyncio.sleep(wait_time)
                    now = time.time()
                    # Clean again after waiting
                    while self._minute_window and now - self._minute_window[0] > 60:
                        self._minute_window.popleft()

            # Check daily limit
            if now - self._day_start > 86400:  # 24 hours
                self._day_start = now
                self._day_count = 0

            if self._day_count >= self.config.requests_per_day:
                wait_time = 86400 - (now - self._day_start)
                logger.error(
                    "rate_limit_daily_exceeded",
                    name=self.name,
                    reset_in_seconds=round(wait_time, 0),
                )
                raise RateLimitExceeded(
                    f"Daily rate limit exceeded for {self.name}. "
                    f"Resets in {wait_time/3600:.1f} hours."
                )

            # Check token limit (for LLM APIs)
            if tokens > 0 and self.config.tokens_per_minute > 0:
                # Clean old token entries
                while self._token_window and now - self._token_window[0][0] > 60:
                    self._token_window.popleft()

                current_tokens = sum(t[1] for t in self._token_window)
                if current_tokens + tokens > self.config.tokens_per_minute:
                    wait_time = 60 - (now - self._token_window[0][0]) if self._token_window else 60
                    logger.warning(
                        "rate_limit_tokens_exceeded",
                        name=self.name,
                        current_tokens=current_tokens,
                        requested_tokens=tokens,
                        waiting_seconds=round(wait_time, 2),
                    )
                    await asyncio.sleep(wait_time)
                    # Clean again after waiting
                    now = time.time()
                    while self._token_window and now - self._token_window[0][0] > 60:
                        self._token_window.popleft()

                self._token_window.append((now, tokens))

            # Record this request
            self._minute_window.append(now)
            self._day_count += 1

    async def __aenter__(self):
        """Async context manager entry."""
        await self._semaphore.acquire()
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self._semaphore.release()
        return False

    def limit(self, tokens_estimator: Optional[Callable[..., int]] = None):
        """Decorator to rate limit an async function.

        Args:
            tokens_estimator: Optional function to estimate tokens from args

        Example:
            @limiter.limit
            async def call_claude(prompt):
                ...

            @limiter.limit(tokens_estimator=lambda p: len(p) // 4)
            async def call_claude(prompt):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                tokens = 0
                if tokens_estimator:
                    try:
                        tokens = tokens_estimator(*args, **kwargs)
                    except Exception:
                        pass

                async with self._semaphore:
                    await self.acquire(tokens)
                    return await func(*args, **kwargs)
            return wrapper
        return decorator

    @property
    def stats(self) -> dict:
        """Get current rate limit statistics."""
        now = time.time()
        return {
            "name": self.name,
            "requests_last_minute": len([t for t in self._minute_window if now - t < 60]),
            "requests_today": self._day_count,
            "tokens_last_minute": sum(t[1] for t in self._token_window if now - t[0] < 60),
            "concurrent_available": self._semaphore._value,
            "limits": {
                "requests_per_minute": self.config.requests_per_minute,
                "requests_per_day": self.config.requests_per_day,
                "tokens_per_minute": self.config.tokens_per_minute,
                "concurrent": self.config.concurrent_requests,
            },
        }


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    pass


# Global rate limiter instances
_limiters: dict[str, RateLimiter] = {}


def get_rate_limiter(name: str, config: Optional[RateLimitConfig] = None) -> RateLimiter:
    """Get or create a rate limiter instance.

    Args:
        name: Name of the API
        config: Optional custom configuration

    Returns:
        RateLimiter instance
    """
    if name not in _limiters:
        _limiters[name] = RateLimiter(name, config)
    return _limiters[name]


def get_all_stats() -> dict[str, dict]:
    """Get statistics for all rate limiters."""
    return {name: limiter.stats for name, limiter in _limiters.items()}
