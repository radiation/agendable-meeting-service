from app.core.logging_config import logger
from app.db.models import MeetingRecurrence
from app.db.repositories.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class MeetingRecurrenceRepository(BaseRepository[MeetingRecurrence]):
    def __init__(self, db: AsyncSession):
        super().__init__(MeetingRecurrence, db)

    async def get_by_id(self, recurrence_id: int) -> MeetingRecurrence:
        logger.debug(f"Fetching recurrence with ID: {recurrence_id}")
        stmt = select(self.model).filter(self.model.id == recurrence_id)
        result = await self.db.execute(stmt)
        recurrence = result.scalars().first()
        if not recurrence:
            logger.warning(f"Recurrence with ID {recurrence_id} not found")
        return recurrence
