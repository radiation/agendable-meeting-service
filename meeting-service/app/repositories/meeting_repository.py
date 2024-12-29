from datetime import datetime

from app.models import Meeting
from app.repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


class MeetingRepository(BaseRepository[Meeting]):
    def __init__(self, db: AsyncSession):
        super().__init__(Meeting, db)

    async def get_meetings_with_recurrence(
        self, recurrence_id: int, after_date: datetime, skip: int = 0, limit: int = 10
    ) -> list[Meeting]:
        stmt = (
            select(self.model)
            .options(joinedload(Meeting.recurrence))
            .filter(
                self.model.recurrence_id == recurrence_id,
                self.model.start_date > after_date,
            )
            .order_by(self.model.start_date)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id_with_recurrence(self, id: int) -> Meeting:
        stmt = (
            select(self.model)
            .options(joinedload(self.model.recurrence))
            .filter(self.model.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_with_recurrence(self, meeting_data: dict) -> Meeting:
        new_meeting = self.model(**meeting_data)
        self.db.add(new_meeting)
        await self.db.commit()
        await self.db.refresh(new_meeting)

        # Eagerly load the recurrence relationship
        stmt = (
            select(self.model)
            .options(joinedload(self.model.recurrence))
            .filter(self.model.id == new_meeting.id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def complete_meeting(self, meeting_id: int) -> Meeting:
        meeting = await self.get_by_id(meeting_id)
        if meeting:
            meeting.completed = True
            await self.db.commit()
            await self.db.refresh(meeting)
        return meeting

    async def batch_create_with_recurrence(
        self, recurrence_id: int, base_meeting: dict, dates: list[datetime]
    ):
        meetings = [
            self.model(
                recurrence_id=recurrence_id,
                start_date=start_date,
                end_date=start_date + base_meeting["duration"],
                **{
                    k: v
                    for k, v in base_meeting.items()
                    if k not in ["start_date", "end_date", "duration"]
                }
            )
            for start_date in dates
        ]
        self.db.add_all(meetings)
        await self.db.commit()
        return meetings
