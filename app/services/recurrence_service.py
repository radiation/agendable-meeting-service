from datetime import datetime

from dateutil.rrule import rrulestr

from app.core.logging_config import logger
from app.db.models.recurrence import Recurrence
from app.db.repositories.recurrence_repo import RecurrenceRepository
from app.schemas.recurrence_schemas import RecurrenceCreate, RecurrenceUpdate
from app.services import BaseService


class RecurrenceService(BaseService[Recurrence, RecurrenceCreate, RecurrenceUpdate]):
    def __init__(self, repo: RecurrenceRepository, redis_client=None):
        super().__init__(repo, redis_client=redis_client)

    async def get_next_meeting_date(
        self, recurrence_id: int, after_date: datetime = datetime.now()
    ) -> datetime:
        logger.info(f"Fetching next meeting date for recurrence ID: {recurrence_id}")
        recurrence = await self.repo.get_by_id(recurrence_id)
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
