from app.db.models import MeetingAttendee
from app.db.repositories.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class MeetingAttendeeRepository(BaseRepository[MeetingAttendee]):
    def __init__(self, db: AsyncSession):
        super().__init__(MeetingAttendee, db)

    async def get_attendees_by_meeting(self, meeting_id: int):
        stmt = select(self.model).filter(self.model.meeting_id == meeting_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_meetings_by_user(self, user_id: int):
        stmt = select(self.model).filter(self.model.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_meeting_and_user(self, meeting_id: int, user_id: int):
        stmt = select(self.model).filter(
            self.model.meeting_id == meeting_id, self.model.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
