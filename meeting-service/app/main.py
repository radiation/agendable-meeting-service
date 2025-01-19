import asyncio
import os
from builtins import anext
from contextlib import asynccontextmanager

from app.api.routes import meeting_routes, recurrence_routes, task_routes, user_routes
from app.core.dependencies import get_db, get_redis_client, get_user_service
from app.core.logging_config import logger
from app.exceptions import (
    NotFoundError,
    ValidationError,
    generic_exception_handler,
    not_found_exception_handler,
    validation_exception_handler,
)
from app.services.redis_subscriber import RedisSubscriber
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

logger.info("Starting application...")


async def test_redis_connection(redis_client):
    try:
        pong = await redis_client.ping()
        if pong:
            logger.info("Redis connection is successful.")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Lifespan startup")

    # Resolve database session manually
    db_session_generator = get_db()  # This is an async generator
    db_session = await anext(db_session_generator)  # Get the first yielded value

    redis_client = get_redis_client()

    user_service = get_user_service(db=db_session, redis=redis_client)

    subscriber = RedisSubscriber(redis_client=redis_client, user_service=user_service)

    app.state.redis_subscriber_task = asyncio.create_task(
        subscriber.listen_to_events("user-events")
    )

    yield

    app.state.redis_subscriber_task.cancel()
    try:
        await app.state.redis_subscriber_task
    except asyncio.CancelledError:
        logger.warning("Redis subscriber task cancelled.")

    await db_session_generator.aclose()  # Close the async generator
    logger.info("Lifespan shutdown complete.")


app = FastAPI(lifespan=lifespan)

# Access the secret key
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the environment variables!")

# Register exception handlers
app.add_exception_handler(NotFoundError, not_found_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers that might use the database internally
app.include_router(meeting_routes.router, prefix="/meetings", tags=["meetings"])
app.include_router(task_routes.router, prefix="/tasks", tags=["tasks"])
app.include_router(user_routes.router, prefix="/users", tags=["users"])
app.include_router(
    recurrence_routes.router,
    prefix="/recurrences",
    tags=["recurrences"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Meeting Service API"}
