import os

from redis.asyncio import Redis


class RedisClient:
    def __init__(self):
        # Load Redis configuration from environment variables
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_password = os.getenv("REDIS_PASSWORD", None)

        # Initialize the Redis client
        self.client = Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            password=self.redis_password,
            decode_responses=True,
        )

    def get_client(self):
        return self.client


# Singleton instance for Redis client
redis_client = RedisClient().get_client()
