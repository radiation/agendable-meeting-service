from datetime import datetime

from app.core.logging_config import logger
from app.db.models import Meeting
from app.db.repositories import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


class MeetingRepository(BaseRepository[Meeting]):
    def __init__(self, db: AsyncSession):
        super().__init__(Meeting, db)

    async def get_meetings_with_recurrence(
        self, recurrence_id: int, after_date: datetime, skip: int = 0, limit: int = 10
    ) -> list[Meeting]:
        logger.debug(
            f"Fetching meetings with recurrence ID {recurrence_id} after {after_date}"
        )
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
        meetings = result.scalars().all()
        logger.debug(
            f"Retrieved {len(meetings)} meetings with recurrence ID {recurrence_id}"
        )
        return meetings

    async def get_meetings_by_user_id(
        self, user_id: int, skip: int = 0, limit: int = 10
    ) -> list[Meeting]:
        logger.debug(
            f"Fetching meetings for user ID: {user_id} with skip={skip}, limit={limit}"
        )
        stmt = (
            select(Meeting)
            .join(Meeting.attendees)
            .options(
                joinedload(Meeting.recurrence),
                joinedload(Meeting.attendees),
            )
            .filter(Meeting.attendees.any(user_id=user_id))
            .order_by(Meeting.start_date)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        meetings = result.scalars().unique().all()
        logger.debug(f"Retrieved {len(meetings)} meetings for user ID {user_id}")
        return meetings

    async def get_by_id_with_recurrence(self, id: int) -> Meeting:
        logger.debug(f"Fetching meeting with ID {id}, including recurrence")
        stmt = (
            select(self.model)
            .options(joinedload(self.model.recurrence))
            .filter(self.model.id == id)
        )
        result = await self.db.execute(stmt)
        meeting = result.scalars().first()
        if not meeting:
            logger.warning(f"Meeting with ID {id} not found")
        return meeting

    async def create_with_recurrence(self, meeting_data: dict) -> Meeting:
        logger.debug(f"Creating meeting with recurrence using data: {meeting_data}")
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
        meeting = result.scalars().first()
        logger.debug(f"Meeting with ID {new_meeting.id} created successfully")
        return meeting

    async def complete_meeting(self, meeting_id: int) -> Meeting:
        logger.debug(f"Marking meeting with ID {meeting_id} as complete")
        meeting = await self.get_by_id(meeting_id)
        if meeting:
            meeting.completed = True
            await self.db.commit()
            await self.db.refresh(meeting)
            logger.debug(f"Meeting with ID {meeting_id} marked as complete")
        else:
            logger.warning(f"Meeting with ID {meeting_id} not found")
        return meeting

    async def batch_create_with_recurrence(
        self, recurrence_id: int, base_meeting: dict, dates: list[datetime]
    ):
        logger.debug(f"Batch creating meetings for recurrence ID {recurrence_id}")
        meetings = [
            self.model(
                recurrence_id=recurrence_id,
                start_date=start_date,
                end_date=start_date + base_meeting["duration"],
                **{
                    k: v
                    for k, v in base_meeting.items()
                    if k not in ["start_date", "end_date", "duration"]
                },
            )
            for start_date in dates
        ]
        self.db.add_all(meetings)
        await self.db.commit()
        logger.debug(
            f"Batch created {len(meetings)} meetings for recurrence ID {recurrence_id}"
        )
        return meetings
