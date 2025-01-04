from app.core.decorators import log_execution_time
from app.core.dependencies import get_meeting_recurrence_service
from app.exceptions import NotFoundError, ValidationError
from app.schemas.meeting_recurrence_schemas import (
    MeetingRecurrenceCreate,
    MeetingRecurrenceRetrieve,
    MeetingRecurrenceUpdate,
)
from app.schemas.meeting_schemas import MeetingRetrieve
from app.services.meeting_recurrence_service import MeetingRecurrenceService
from fastapi import APIRouter, Depends
from loguru import logger

router = APIRouter()


# Create a new meeting recurrence
@router.post("/", response_model=MeetingRecurrenceRetrieve)
@log_execution_time
async def create_meeting_recurrence(
    meeting_recurrence: MeetingRecurrenceCreate,
    service: MeetingRecurrenceService = Depends(get_meeting_recurrence_service),
) -> MeetingRecurrenceRetrieve:
    logger.info(
        f"Creating meeting recurrence with data: {meeting_recurrence.model_dump()}"
    )
    try:
        result = await service.create(meeting_recurrence)
        logger.info(f"Meeting recurrence created successfully with ID: {result.id}")
        return result
    except ValidationError as ve:
        logger.warning(f"Validation error: {ve}")
        raise
    except Exception:
        logger.exception("Unexpected error while creating meeting recurrence")
        raise ValidationError(detail="An unexpected error occurred. Please try again.")


# List all meeting recurrences
@router.get("/", response_model=list[MeetingRecurrenceRetrieve])
@log_execution_time
async def get_meeting_recurrences(
    skip: int = 0,
    limit: int = 10,
    service: MeetingRecurrenceService = Depends(get_meeting_recurrence_service),
) -> list[MeetingRecurrenceRetrieve]:
    logger.info(f"Fetching all meeting recurrences with skip={skip} and limit={limit}")
    result = await service.get_all(skip=skip, limit=limit)
    logger.info(f"Retrieved {len(result)} meeting recurrences.")
    return result


# Get a meeting recurrence by ID
@router.get(
    "/{recurrence_id}",
    response_model=MeetingRecurrenceRetrieve,
)
@log_execution_time
async def get_meeting_recurrence(
    recurrence_id: int,
    service: MeetingRecurrenceService = Depends(get_meeting_recurrence_service),
) -> MeetingRecurrenceRetrieve:
    logger.info(f"Fetching meeting recurrence with ID: {recurrence_id}")
    result = await service.get_by_id(recurrence_id)
    if result is None:
        logger.warning(f"Meeting recurrence with ID {recurrence_id} not found")
        raise NotFoundError(detail="Meeting recurrence not found")
    logger.info(f"Meeting recurrence retrieved: {result}")
    return result


# Update an existing meeting recurrence
@router.put(
    "/{recurrence_id}",
    response_model=MeetingRecurrenceRetrieve,
)
@log_execution_time
async def update_meeting_recurrence(
    recurrence_id: int,
    meeting_recurrence: MeetingRecurrenceUpdate,
    service: MeetingRecurrenceService = Depends(get_meeting_recurrence_service),
) -> MeetingRecurrenceRetrieve:
    logger.info(
        f"Updating meeting recurrence with ID: {recurrence_id} \
            with data: {meeting_recurrence.model_dump()}"
    )
    result = await service.update(recurrence_id, meeting_recurrence)
    if result is None:
        logger.warning(f"Meeting recurrence with ID {recurrence_id} not found")
        raise NotFoundError(detail="Meeting recurrence not found")
    logger.info(f"Meeting recurrence updated successfully: {result}")
    return result


# Delete a meeting recurrence
@router.delete("/{recurrence_id}", status_code=204)
@log_execution_time
async def delete_meeting_recurrence(
    recurrence_id: int,
    service: MeetingRecurrenceService = Depends(get_meeting_recurrence_service),
) -> None:
    logger.info(f"Deleting meeting recurrence with ID: {recurrence_id}")
    success = await service.delete(recurrence_id)
    if not success:
        logger.warning(f"Meeting recurrence with ID {recurrence_id} not found")
        raise NotFoundError(detail="Meeting recurrence not found")


# Get the next meeting for a recurrence
@router.get("/next-meeting/{recurrence_id}", response_model=MeetingRetrieve)
@log_execution_time
async def next_meeting(
    recurrence_id: int,
    service: MeetingRecurrenceService = Depends(get_meeting_recurrence_service),
) -> MeetingRetrieve:
    logger.info(f"Fetching next meeting for recurrence with ID: {recurrence_id}")
    next_meeting_date = await service.get_next_meeting_date(recurrence_id)
    if not next_meeting_date:
        logger.warning("No next meeting found or invalid recurrence")
        raise NotFoundError(detail="No next meeting found or invalid recurrence")
    logger.info(f"Next meeting date: {next_meeting_date}")
    return next_meeting_date
