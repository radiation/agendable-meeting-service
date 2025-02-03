from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.recurrence import Recurrence
from app.db.repositories import BaseRepository


class RecurrenceRepository(BaseRepository[Recurrence]):
    def __init__(self, db: AsyncSession):
        super().__init__(Recurrence, db)
