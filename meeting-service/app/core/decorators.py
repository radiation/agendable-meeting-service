import time
from functools import wraps

from loguru import logger


# Utility function to log execution time
def log_execution_time(func):
    @wraps(func)  # This preserves the original function's signature
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.info(f"{func.__name__} executed in {elapsed_time:.2f} seconds")
        return result

    return wrapper
