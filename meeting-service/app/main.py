import os

from app.api.routers import (
    meeting_attendee_router,
    meeting_recurrence_router,
    meeting_router,
    meeting_task_router,
    task_router,
)
from app.errors import (
    NotFoundError,
    ValidationError,
    generic_exception_handler,
    not_found_exception_handler,
    validation_exception_handler,
)
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app = FastAPI()

# Access the secret key
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the environment variables!")

# Register exception handlers
app.add_exception_handler(NotFoundError, not_found_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers that might use the database internally
app.include_router(meeting_router.router, prefix="/meetings", tags=["meetings"])
app.include_router(task_router.router, prefix="/tasks", tags=["tasks"])
app.include_router(
    meeting_task_router.router, prefix="/meeting_tasks", tags=["meeting_tasks"]
)
app.include_router(
    meeting_attendee_router.router,
    prefix="/meeting_attendees",
    tags=["meeting_attendees"],
)
app.include_router(
    meeting_recurrence_router.router,
    prefix="/meeting_recurrences",
    tags=["meeting_recurrences"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Meeting Service API"}
