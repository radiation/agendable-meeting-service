import re

from app.db import get_db
from app.exceptions import ForbiddenError, ValidationError
from app.services.meeting_attendee_service import get_meeting_attendee_service
from app.utils.auth import get_user_metadata
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def extract_meeting_id(path: str) -> int:
    """Extracts the meeting ID from the request path."""
    match = re.search(r"/meetings/(\d+)", path)
    if match:
        return int(match.group(1))
    return None


async def meeting_permission_middleware(request: Request, call_next):
    """Middleware to enforce meeting-specific permissions."""
    if request.url.path.startswith("/meetings/") and request.method != "POST":
        # Extract user metadata
        user_metadata = get_user_metadata(request)
        user_id = user_metadata.get("user_id")
        if not user_id:
            raise ValidationError(detail="User ID is missing in request metadata.")

        # Attach user_id to the request state
        request.state.user_id = user_id

        # Extract meeting_id from the path
        meeting_id = await extract_meeting_id(request.url.path)
        if not meeting_id:
            raise ValidationError(detail="Invalid meeting ID in path.")

        # Validate attendee via service layer
        db: AsyncSession = await get_db()
        try:
            attendee = await get_meeting_attendee_service(db, meeting_id, user_id)
        except Exception:
            raise ForbiddenError(
                detail="You are not authorized to access this meeting."
            )

        # Attach attendee to the request state
        request.state.attendee = attendee

    return await call_next(request)
