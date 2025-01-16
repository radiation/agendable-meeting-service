import os

from app.api.routes import (
    attendee_routes,
    meeting_recurrence_routes,
    meeting_routes,
    meeting_task_routes,
    task_routes,
)
from app.core.logging_config import logger
from app.exceptions import (
    NotFoundError,
    ValidationError,
    generic_exception_handler,
    not_found_exception_handler,
    validation_exception_handler,
)
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

logger.info("Starting application...")

app = FastAPI()

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
app.include_router(
    meeting_task_routes.router, prefix="/meeting_tasks", tags=["meeting_tasks"]
)
app.include_router(
    attendee_routes.router,
    prefix="/attendees",
    tags=["attendees"],
)
app.include_router(
    meeting_recurrence_routes.router,
    prefix="/meeting_recurrences",
    tags=["meeting_recurrences"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Meeting Service API"}
