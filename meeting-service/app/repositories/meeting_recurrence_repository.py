from app.models import MeetingRecurrence
from app.repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class MeetingRecurrenceRepository(BaseRepository[MeetingRecurrence]):
    def __init__(self, db: AsyncSession):
        super().__init__(MeetingRecurrence, db)

    async def get_by_id(self, recurrence_id: int) -> MeetingRecurrence:
        stmt = select(self.model).filter(self.model.id == recurrence_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
