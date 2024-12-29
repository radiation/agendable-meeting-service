from app.models import MeetingAttendee
from app.repositories.meeting_attendee_repository import MeetingAttendeeRepository
from app.schemas.meeting_attendee_schemas import (
    MeetingAttendeeCreate,
    MeetingAttendeeUpdate,
)
from app.services.base import BaseService


class MeetingAttendeeService(
    BaseService[MeetingAttendee, MeetingAttendeeCreate, MeetingAttendeeUpdate]
):
    def __init__(self, repository: MeetingAttendeeRepository):
        super().__init__(repository)
