from app.core.dependencies import get_meeting_recurrence_service
from app.exceptions import NotFoundError
from app.schemas import meeting_recurrence_schemas, meeting_schemas
from app.services.meeting_recurrence_service import MeetingRecurrenceService
from fastapi import APIRouter, Depends

router = APIRouter()


# Create a new meeting recurrence
@router.post("/", response_model=meeting_recurrence_schemas.MeetingRecurrenceRetrieve)
async def create_meeting_recurrence(
    meeting_recurrence: meeting_recurrence_schemas.MeetingRecurrenceCreate,
    service: MeetingRecurrenceService = Depends(get_meeting_recurrence_service),
) -> meeting_recurrence_schemas.MeetingRecurrenceRetrieve:
    return await service.create(meeting_recurrence)


# List all meeting recurrences
@router.get(
    "/", response_model=list[meeting_recurrence_schemas.MeetingRecurrenceRetrieve]
)
async def get_meeting_recurrences(
    skip: int = 0,
    limit: int = 10,
    service: MeetingRecurrenceService = Depends(get_meeting_recurrence_service),
) -> list[meeting_recurrence_schemas.MeetingRecurrenceRetrieve]:
    recurrences = await service.get_all(skip=skip, limit=limit)
    return [
        meeting_recurrence_schemas.MeetingRecurrenceRetrieve.model_validate(recurrence)
        for recurrence in recurrences
    ]


# Get a meeting recurrence by ID
@router.get(
    "/{recurrence_id}",
    response_model=meeting_recurrence_schemas.MeetingRecurrenceRetrieve,
)
async def get_meeting_recurrence(
    recurrence_id: int,
    service: MeetingRecurrenceService = Depends(get_meeting_recurrence_service),
) -> meeting_recurrence_schemas.MeetingRecurrenceRetrieve:
    return await service.get_by_id(recurrence_id)


# Update an existing meeting recurrence
@router.put(
    "/{recurrence_id}",
    response_model=meeting_recurrence_schemas.MeetingRecurrenceRetrieve,
)
async def update_meeting_recurrence(
    recurrence_id: int,
    meeting_recurrence: meeting_recurrence_schemas.MeetingRecurrenceUpdate,
    service: MeetingRecurrenceService = Depends(get_meeting_recurrence_service),
) -> meeting_recurrence_schemas.MeetingRecurrenceRetrieve:
    return await service.update(recurrence_id, meeting_recurrence)


# Delete a meeting recurrence
@router.delete("/{recurrence_id}", status_code=204)
async def delete_meeting_recurrence(
    recurrence_id: int,
    service: MeetingRecurrenceService = Depends(get_meeting_recurrence_service),
):
    await service.delete(recurrence_id)
    return {"detail": "Meeting recurrence deleted successfully"}


# Get the next meeting for a recurrence
@router.get(
    "/next-meeting/{recurrence_id}", response_model=meeting_schemas.MeetingRetrieve
)
async def next_meeting(
    recurrence_id: int,
    service: MeetingRecurrenceService = Depends(get_meeting_recurrence_service),
):
    next_meeting_date = await service.get_next_meeting_date(recurrence_id)
    if not next_meeting_date:
        raise NotFoundError(detail="No next meeting found or invalid recurrence")
    return next_meeting_date
