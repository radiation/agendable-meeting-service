from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.logging_config import logger
from app.db.models.meeting import Meeting
from app.db.models.relationships import meeting_users
from app.db.models.user import User
from app.db.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_users_by_meeting(self, meeting_id: int) -> list[User]:
        logger.debug(f"Fetching attendees for meeting ID: {meeting_id}")
        stmt = (
            select(User)
            .join(meeting_users)
            .filter(meeting_users.c.meeting_id == meeting_id)
        )
        result = await self.db.execute(stmt)
        Users = list(result.scalars().all())
        logger.debug(f"Retrieved {len(Users)} Users for meeting ID: {meeting_id}")
        return Users

    async def get_meetings_by_user(self, user_id: int) -> list[Meeting]:
        logger.debug(f"Fetching meetings for user ID: {user_id}")
        stmt = (
            select(Meeting)
            .join(meeting_users)
            .filter(meeting_users.c.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        meetings = list(result.scalars().all())
        logger.debug(f"Retrieved {len(meetings)} meetings for user ID: {user_id}")
        return meetings

    async def get_by_meeting_and_user(
        self, meeting_id: int, user_id: int
    ) -> Optional[User]:
        logger.debug(
            f"Fetching user with meeting ID: {meeting_id} and user ID: {user_id}"
        )
        stmt = (
            select(User)
            .join(meeting_users)
            .filter(
                meeting_users.c.meeting_id == meeting_id,
                meeting_users.c.user_id == user_id,
            )
        )
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        if not user:
            logger.warning(
                f"No user found for meeting ID {meeting_id} and user ID {user_id}"
            )
        return user
