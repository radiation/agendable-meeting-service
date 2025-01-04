from app.core.logging_config import logger
from app.db.models import MeetingAttendee
from app.db.repositories.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class MeetingAttendeeRepository(BaseRepository[MeetingAttendee]):
    def __init__(self, db: AsyncSession):
        super().__init__(MeetingAttendee, db)

    async def get_attendees_by_meeting(self, meeting_id: int):
        logger.debug(f"Fetching attendees for meeting ID: {meeting_id}")
        stmt = select(self.model).filter(self.model.meeting_id == meeting_id)
        result = await self.db.execute(stmt)
        attendees = result.scalars().all()
        logger.debug(
            f"Retrieved {len(attendees)} attendees for meeting ID: {meeting_id}"
        )
        return attendees

    async def get_meetings_by_user(self, user_id: int):
        logger.debug(f"Fetching meetings for user ID: {user_id}")
        stmt = select(self.model).filter(self.model.user_id == user_id)
        result = await self.db.execute(stmt)
        meetings = result.scalars().all()
        logger.debug(f"Retrieved {len(meetings)} meetings for user ID: {user_id}")
        return meetings

    async def get_by_meeting_and_user(self, meeting_id: int, user_id: int):
        logger.debug(
            f"Fetching attendee with meeting ID: {meeting_id} and user ID: {user_id}"
        )
        stmt = select(self.model).filter(
            self.model.meeting_id == meeting_id, self.model.user_id == user_id
        )
        result = await self.db.execute(stmt)
        attendee = result.scalars().first()
        if not attendee:
            logger.warning(
                f"No attendee found for meeting ID {meeting_id} and user ID {user_id}"
            )
        return attendee
