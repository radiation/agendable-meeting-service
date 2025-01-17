from app.core.logging_config import logger
from app.db.models import User
from app.db.repositories.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_Users_by_meeting(self, meeting_id: int):
        logger.debug(f"Fetching attendees for meeting ID: {meeting_id}")
        stmt = select(self.model).filter(self.model.meeting_id == meeting_id)
        result = await self.db.execute(stmt)
        Users = result.scalars().all()
        logger.debug(f"Retrieved {len(Users)} Users for meeting ID: {meeting_id}")
        return Users

    async def get_meetings_by_user(self, user_id: int):
        logger.debug(f"Fetching meetings for user ID: {user_id}")
        stmt = select(self.model).filter(self.model.id == user_id)
        result = await self.db.execute(stmt)
        meetings = result.scalars().all()
        logger.debug(f"Retrieved {len(meetings)} meetings for user ID: {user_id}")
        return meetings

    async def get_by_meeting_and_user(self, meeting_id: int, user_id: int):
        logger.debug(
            f"Fetching user with meeting ID: {meeting_id} and user ID: {user_id}"
        )
        stmt = select(self.model).filter(
            self.model.meeting_id == meeting_id, self.model.user_id == user_id
        )
        result = await self.db.execute(stmt)
        User = result.scalars().first()
        if not User:
            logger.warning(
                f"No user found for meeting ID {meeting_id} and user ID {user_id}"
            )
        return User
