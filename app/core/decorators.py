from functools import wraps
import time
from typing import Any, Awaitable, Callable, TypeVar

from loguru import logger

T = TypeVar("T", bound=Callable[..., Awaitable[Any]])


# Utility function to log execution time
def log_execution_time(func: T) -> T:
    """Decorator to log the execution time of a function."""

    @wraps(func)  # This preserves the original function's signature
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.info(f"{func.__name__} executed in {elapsed_time:.2f} seconds")
        return result

    return wrapper
