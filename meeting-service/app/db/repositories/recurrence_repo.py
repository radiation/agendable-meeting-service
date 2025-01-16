from app.core.logging_config import logger
from app.db.models import Recurrence
from app.db.repositories.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class RecurrenceRepository(BaseRepository[Recurrence]):
    def __init__(self, db: AsyncSession):
        super().__init__(Recurrence, db)

    async def get_by_id(self, recurrence_id: int) -> Recurrence:
        logger.debug(f"Fetching recurrence with ID: {recurrence_id}")
        stmt = select(self.model).filter(self.model.id == recurrence_id)
        result = await self.db.execute(stmt)
        recurrence = result.scalars().first()
        if not recurrence:
            logger.warning(f"Recurrence with ID {recurrence_id} not found")
        return recurrence
