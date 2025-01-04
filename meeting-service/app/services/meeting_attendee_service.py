from app.db.models import MeetingAttendee
from app.db.repositories.meeting_attendee_repo import MeetingAttendeeRepository
from app.schemas.meeting_attendee_schemas import (
    MeetingAttendeeCreate,
    MeetingAttendeeUpdate,
)
from app.services.base_service import BaseService


class MeetingAttendeeService(
    BaseService[MeetingAttendee, MeetingAttendeeCreate, MeetingAttendeeUpdate]
):
    def __init__(self, repo: MeetingAttendeeRepository):
        super().__init__(repo, model_name="MeetingAttendee")
