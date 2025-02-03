import os

from dotenv import load_dotenv
import redis.asyncio as redis

# Load environment variables from .env
load_dotenv()

# Retrieve Redis connection details
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

redis_url = (
    f"redis://{REDIS_PASSWORD + '@' if REDIS_PASSWORD else ''}"
    f"{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
)

# Initialize the Redis client
redis_client = redis.from_url(redis_url, decode_responses=True)
