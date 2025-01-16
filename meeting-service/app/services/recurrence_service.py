from datetime import datetime

from app.core.logging_config import logger
from app.db.models import Recurrence
from app.db.repositories import RecurrenceRepository
from app.schemas import RecurrenceCreate, RecurrenceUpdate
from app.services import BaseService
from dateutil.rrule import rrulestr


class RecurrenceService(BaseService[Recurrence, RecurrenceCreate, RecurrenceUpdate]):
    def __init__(self, repo: RecurrenceRepository):
        super().__init__(repo, model_name="Recurrence")

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
