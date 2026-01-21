"""Async utilities for safe execution of coroutines in sync contexts.

This module provides helpers for running async code from synchronous contexts,
particularly useful for Celery tasks and other sync-first frameworks.

Usage:
    from core.async_utils import run_async

    # In a sync function (e.g., Celery task)
    result = run_async(some_async_function(arg1, arg2))
"""

import asyncio
from typing import TypeVar, Coroutine, Any
from functools import wraps
import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Run an async coroutine from a synchronous context safely.

    This function handles the event loop lifecycle properly to avoid
    issues with nested event loops and resource cleanup.

    Args:
        coro: The coroutine to run

    Returns:
        The result of the coroutine

    Example:
        async def fetch_data():
            return await some_api_call()

        # In sync code:
        result = run_async(fetch_data())
    """
    try:
        # Check if there's already a running loop
        loop = asyncio.get_running_loop()
        # If we're already in an async context, this would be a problem
        # but we'll try to handle it gracefully
        logger.warning(
            "run_async_called_in_async_context",
            msg="Consider using await directly instead of run_async",
        )
        # Create a new thread to run the coroutine
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No running loop, safe to create one
        pass

    # Create and run in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        # Clean up properly
        try:
            # Cancel all pending tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            # Allow tasks to be cancelled
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            asyncio.set_event_loop(None)
            loop.close()


def async_to_sync(func):
    """Decorator to convert an async function to sync.

    Useful for making async functions callable from sync contexts.

    Example:
        @async_to_sync
        async def my_async_function(x, y):
            return await some_async_call(x, y)

        # Now can be called synchronously:
        result = my_async_function(1, 2)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return run_async(func(*args, **kwargs))
    return wrapper


class AsyncContextManager:
    """Context manager for running multiple async operations.

    Useful when you need to run multiple async operations in a sync context
    while sharing the same event loop.

    Example:
        with AsyncContextManager() as ctx:
            result1 = ctx.run(async_op1())
            result2 = ctx.run(async_op2())
    """

    def __init__(self):
        self._loop = None

    def __enter__(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._loop:
            try:
                pending = asyncio.all_tasks(self._loop)
                for task in pending:
                    task.cancel()
                if pending:
                    self._loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
                self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            finally:
                asyncio.set_event_loop(None)
                self._loop.close()
        return False

    def run(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run a coroutine in the managed event loop."""
        if not self._loop:
            raise RuntimeError("AsyncContextManager not entered")
        return self._loop.run_until_complete(coro)


async def gather_with_concurrency(
    n: int,
    *coros: Coroutine[Any, Any, T],
) -> list[T]:
    """Run coroutines with limited concurrency.

    Useful for rate-limiting API calls.

    Args:
        n: Maximum number of concurrent coroutines
        *coros: Coroutines to run

    Returns:
        List of results in order

    Example:
        results = await gather_with_concurrency(
            5,  # Max 5 concurrent
            fetch_company(id1),
            fetch_company(id2),
            fetch_company(id3),
            # ... more
        )
    """
    semaphore = asyncio.Semaphore(n)

    async def sem_coro(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(sem_coro(c) for c in coros))
