from datetime import datetime

from app.db.models import MeetingRecurrence
from app.db.repositories.meeting_recurrence_repo import MeetingRecurrenceRepository
from app.schemas.meeting_recurrence_schemas import (
    MeetingRecurrenceCreate,
    MeetingRecurrenceUpdate,
)
from app.services.base_service import BaseService
from dateutil.rrule import rrulestr
from loguru import logger


class MeetingRecurrenceService(
    BaseService[MeetingRecurrence, MeetingRecurrenceCreate, MeetingRecurrenceUpdate]
):
    def __init__(self, repo: MeetingRecurrenceRepository):
        super().__init__(repo, model_name="MeetingRecurrence")

    async def get_next_meeting_date(
        self, recurrence_id: int, after_date: datetime = datetime.now()
    ) -> datetime:
        logger.info(f"Fetching next meeting date for recurrence ID: {recurrence_id}")
        recurrence = await self.recurrence_repo.get_by_id(recurrence_id)
        if not recurrence:
            logger.warning(f"Recurrence with ID {recurrence_id} not found")
            return None

        rule = rrulestr(recurrence.rrule, dtstart=after_date)
        try:
            next_meeting_date = list(rule[:1])[0]
            logger.info(
                f"Next meeting date for recurrence ID \
                    {recurrence_id}: {next_meeting_date}"
            )
            return next_meeting_date
        except StopIteration:
            logger.warning(f"No meeting date found after {after_date}")
            return None
