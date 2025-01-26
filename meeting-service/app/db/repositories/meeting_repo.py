from datetime import datetime
from uuid import UUID

from app.core.logging_config import logger
from app.db.models import Meeting, User, meeting_users
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
        self, user_id: UUID, skip: int = 0, limit: int = 10
    ) -> list[Meeting]:
        logger.debug(
            f"Fetching meetings for user ID: {user_id} with skip={skip}, limit={limit}"
        )
        # TODO: Filter by user ID
        stmt = (
            select(Meeting)
            .options(
                joinedload(Meeting.recurrence),
            )
            .order_by(Meeting.start_date)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        meetings = result.scalars().unique().all()
        logger.debug(f"Retrieved {len(meetings)} meetings for user ID {user_id}")
        return meetings

    async def add_users_to_meeting(self, meeting_id: int, user_ids: list[UUID]):
        logger.info(f"Adding users to meeting ID {meeting_id}: {user_ids}")

        try:
            # Check for existing records
            for user_id in user_ids:
                query = select(meeting_users).where(
                    (meeting_users.c.meeting_id == meeting_id)
                    & (meeting_users.c.user_id == user_id)
                )
                result = await self.db.execute(query)
                existing = result.scalar_one_or_none()

                if not existing:
                    new_entry = {"meeting_id": meeting_id, "user_id": user_id}
                    stmt = meeting_users.insert().values(new_entry)
                    await self.db.execute(stmt)

            await self.db.commit()
            logger.info(f"Successfully added users to meeting ID {meeting_id}")
        except Exception as e:
            logger.exception(f"Error adding users to meeting ID {meeting_id}: {e}")
            raise

    async def get_users_from_meeting(self, meeting_id: int):
        logger.info(f"Fetching users for meeting ID {meeting_id}")

        try:
            # Join meeting_users with users to fetch user details
            stmt = (
                select(User)
                .join(meeting_users, User.id == meeting_users.c.user_id)
                .where(meeting_users.c.meeting_id == meeting_id)
            )

            result = await self.db.execute(stmt)
            users = result.scalars().all()
            logger.info(f"Found {len(users)} users for meeting ID {meeting_id}")
            return users
        except Exception as e:
            logger.exception(f"Error fetching users for meeting ID {meeting_id}: {e}")
            raise

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
