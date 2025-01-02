from typing import List

from app.core.dependencies import get_meeting_attendee_service
from app.schemas import meeting_attendee_schemas, meeting_schemas
from app.services.meeting_attendee_service import MeetingAttendeeService
from fastapi import APIRouter, Depends, Header

router = APIRouter()


@router.post("/", response_model=meeting_attendee_schemas.MeetingAttendeeRetrieve)
async def create_meeting_attendee(
    attendee: meeting_attendee_schemas.MeetingAttendeeCreate,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
) -> meeting_attendee_schemas.MeetingAttendeeRetrieve:
    return await service.create(attendee)


@router.get("/", response_model=List[meeting_attendee_schemas.MeetingAttendeeRetrieve])
async def get_meeting_attendees(
    skip: int = 0,
    limit: int = 10,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
) -> List[meeting_attendee_schemas.MeetingAttendeeRetrieve]:
    return await service.get_all(skip, limit)


@router.get(
    "/{meeting_attendee_id}",
    response_model=meeting_attendee_schemas.MeetingAttendeeRetrieve,
)
async def get_meeting_attendee(
    meeting_attendee_id: int,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
) -> meeting_attendee_schemas.MeetingAttendeeRetrieve:
    return await service.get_by_id(meeting_attendee_id)


@router.put(
    "/{meeting_attendee_id}",
    response_model=meeting_attendee_schemas.MeetingAttendeeRetrieve,
)
async def update_meeting_attendee(
    meeting_attendee_id: int,
    attendee: meeting_attendee_schemas.MeetingAttendeeUpdate,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
) -> meeting_attendee_schemas.MeetingAttendeeRetrieve:
    return await service.update(meeting_attendee_id, attendee)


@router.delete("/{meeting_attendee_id}", status_code=204)
async def delete_meeting_attendee(
    meeting_attendee_id: int,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
):
    return await service.delete(meeting_attendee_id)


@router.get(
    "/by_meeting/{meeting_id}",
    response_model=List[meeting_attendee_schemas.MeetingAttendeeRetrieve],
)
async def get_attendees_by_meeting(
    meeting_id: int,
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
) -> List[meeting_attendee_schemas.MeetingAttendeeRetrieve]:
    return await service.get_by_field(field_name="meeting_id", value=meeting_id)


@router.get(
    "/user_meetings/{user_id}", response_model=List[meeting_schemas.MeetingRetrieve]
)
async def get_meetings_by_user(
    user_id: int,
    authorization: str = Header(None),
    service: MeetingAttendeeService = Depends(get_meeting_attendee_service),
) -> List[meeting_schemas.MeetingRetrieve]:
    print(f"Authorization header received: {authorization}")
    return await service.get_by_field(field_name="user_id", value=user_id)
