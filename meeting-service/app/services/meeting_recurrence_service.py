from datetime import datetime

from app.db.models import MeetingRecurrence
from app.db.repositories.meeting_recurrence_repo import MeetingRecurrenceRepository
from app.schemas.meeting_recurrence_schemas import (
    MeetingRecurrenceCreate,
    MeetingRecurrenceUpdate,
)
from app.services.base_service import BaseService
from dateutil.rrule import rrulestr


class MeetingRecurrenceService(
    BaseService[MeetingRecurrence, MeetingRecurrenceCreate, MeetingRecurrenceUpdate]
):
    def __init__(self, repo: MeetingRecurrenceRepository):
        super().__init__(repo)

    async def get_next_meeting_date(
        self, recurrence_id: int, after_date: datetime = datetime.now()
    ) -> datetime:
        recurrence = await self.recurrence_repo.get_by_id(recurrence_id)
        if not recurrence:
            return None

        rule = rrulestr(recurrence.rrule, dtstart=after_date)
        try:
            next_meeting_date = list(rule[:1])[0]
            return next_meeting_date
        except StopIteration:
            return None
