from typing import List

from app.core.decorators import log_execution_time
from app.core.dependencies import get_meeting_attendee_service
from app.exceptions import NotFoundError, ValidationError
from app.schemas.meeting_attendee_schemas import (
    MeetingAttendeeCreate,
    MeetingAttendeeRetrieve,
    MeetingAttendeeUpdate,
)
from app.services.meeting_attendee_service import MeetingAttendeeService
from fastapi import APIRouter, Depends
from loguru import logger

router = APIRouter()


@router.post("/", response_model=MeetingAttendeeRetrieve)
@log_execution_time
async def create_meeting_attendee(
    attendee: MeetingAttendeeCreate,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
) -> MeetingAttendeeRetrieve:
    logger.info(f"Creating meeting attendee with data: {attendee.model_dump()}")
    try:
        result = await service.create(attendee)
        logger.info(f"Meeting attendee created successfully with ID: {result.id}")
        return result
    except ValidationError as ve:
        logger.warning(f"Validation error: {ve}")
        raise
    except Exception:
        logger.exception("Unexpected error while creating meeting attendee")
        raise ValidationError(detail="An unexpected error occurred. Please try again.")


@router.get("/", response_model=List[MeetingAttendeeRetrieve])
@log_execution_time
async def get_meeting_attendees(
    skip: int = 0,
    limit: int = 10,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
) -> List[MeetingAttendeeRetrieve]:
    logger.info(f"Fetching all meeting attendees with skip={skip} and limit={limit}")
    result = await service.get_all(skip, limit)
    logger.info(f"Retrieved {len(result)} meeting attendees.")
    return result


@router.get(
    "/{meeting_attendee_id}",
    response_model=MeetingAttendeeRetrieve,
)
@log_execution_time
async def get_meeting_attendee(
    meeting_attendee_id: int,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
) -> MeetingAttendeeRetrieve:
    logger.info(f"Fetching meeting attendee with ID: {meeting_attendee_id}")
    result = await service.get_by_id(meeting_attendee_id)
    if result is None:
        logger.warning(f"Meeting attendee with ID {meeting_attendee_id} not found")
        raise NotFoundError(detail="Meeting attendee not found")
    logger.info(f"Meeting attendee retrieved: {result}")
    return result


@router.put(
    "/{meeting_attendee_id}",
    response_model=MeetingAttendeeRetrieve,
)
@log_execution_time
async def update_meeting_attendee(
    meeting_attendee_id: int,
    attendee: MeetingAttendeeUpdate,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
) -> MeetingAttendeeRetrieve:
    logger.info(
        f"Updating meeting attendee with ID: {meeting_attendee_id} \
            with data: {attendee.model_dump()}"
    )
    result = await service.update(meeting_attendee_id, attendee)
    if result is None:
        logger.warning(f"Meeting attendee with ID {meeting_attendee_id} not found")
        raise NotFoundError(detail="Meeting attendee not found")
    logger.info(f"Meeting attendee updated successfully: {result}")
    return result


@router.delete("/{meeting_attendee_id}", status_code=204)
@log_execution_time
async def delete_meeting_attendee(
    meeting_attendee_id: int,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
) -> None:
    logger.info(f"Deleting meeting attendee with ID: {meeting_attendee_id}")
    success = await service.delete(meeting_attendee_id)
    if not success:
        logger.warning(f"Meeting attendee with ID {meeting_attendee_id} not found")
        raise NotFoundError(detail="Meeting attendee not found")


@router.get(
    "/by_meeting/{meeting_id}",
    response_model=List[MeetingAttendeeRetrieve],
)
@log_execution_time
async def get_attendees_by_meeting(
    meeting_id: int,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
) -> List[MeetingAttendeeRetrieve]:
    logger.info(f"Fetching all meeting attendees for meeting with ID: {meeting_id}")
    result = await service.get_by_field(field_name="meeting_id", value=meeting_id)
    logger.info(
        f"Retrieved {len(result)} meeting attendees for meeting ID: {meeting_id}"
    )
    return result
