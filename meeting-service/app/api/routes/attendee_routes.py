from typing import List

from app.core.decorators import log_execution_time
from app.core.dependencies import get_attendee_service
from app.core.logging_config import logger
from app.exceptions import NotFoundError, ValidationError
from app.schemas.attendee_schemas import (
    AttendeeCreate,
    AttendeeRetrieve,
    AttendeeUpdate,
)
from app.services.attendee_service import AttendeeService
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/", response_model=AttendeeRetrieve)
@log_execution_time
async def create_attendee(
    attendee: AttendeeCreate,
    service: AttendeeService = Depends(get_attendee_service),
) -> AttendeeRetrieve:
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


@router.get("/", response_model=List[AttendeeRetrieve])
@log_execution_time
async def get_attendees(
    skip: int = 0,
    limit: int = 10,
    service: AttendeeService = Depends(get_attendee_service),
) -> List[AttendeeRetrieve]:
    logger.info(f"Fetching all meeting attendees with skip={skip} and limit={limit}")
    result = await service.get_all(skip, limit)
    logger.info(f"Retrieved {len(result)} meeting attendees.")
    return result


@router.get(
    "/{attendee_id}",
    response_model=AttendeeRetrieve,
)
@log_execution_time
async def get_attendee(
    attendee_id: int,
    service: AttendeeService = Depends(get_attendee_service),
) -> AttendeeRetrieve:
    logger.info(f"Fetching meeting attendee with ID: {attendee_id}")
    result = await service.get_by_id(attendee_id)
    if result is None:
        logger.warning(f"Meeting attendee with ID {attendee_id} not found")
        raise NotFoundError(detail="Meeting attendee not found")
    logger.info(f"Meeting attendee retrieved: {result}")
    return result


@router.put(
    "/{attendee_id}",
    response_model=AttendeeRetrieve,
)
@log_execution_time
async def update_attendee(
    attendee_id: int,
    attendee: AttendeeUpdate,
    service: AttendeeService = Depends(get_attendee_service),
) -> AttendeeRetrieve:
    logger.info(
        f"Updating meeting attendee with ID: {attendee_id} \
            with data: {attendee.model_dump()}"
    )
    result = await service.update(attendee_id, attendee)
    if result is None:
        logger.warning(f"Meeting attendee with ID {attendee_id} not found")
        raise NotFoundError(detail="Meeting attendee not found")
    logger.info(f"Meeting attendee updated successfully: {result}")
    return result


@router.delete("/{attendee_id}", status_code=204)
@log_execution_time
async def delete_attendee(
    attendee_id: int,
    service: AttendeeService = Depends(get_attendee_service),
) -> None:
    logger.info(f"Deleting meeting attendee with ID: {attendee_id}")
    success = await service.delete(attendee_id)
    if not success:
        logger.warning(f"Meeting attendee with ID {attendee_id} not found")
        raise NotFoundError(detail="Meeting attendee not found")


@router.get(
    "/by_meeting/{meeting_id}",
    response_model=List[AttendeeRetrieve],
)
@log_execution_time
async def get_attendees_by_meeting(
    meeting_id: int,
    service: AttendeeService = Depends(get_attendee_service),
) -> List[AttendeeRetrieve]:
    logger.info(f"Fetching all meeting attendees for meeting with ID: {meeting_id}")
    result = await service.get_by_field(field_name="meeting_id", value=meeting_id)
    logger.info(
        f"Retrieved {len(result)} meeting attendees for meeting ID: {meeting_id}"
    )
    return result
