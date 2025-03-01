from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.logging_config import logger
from app.db.models.meeting import Meeting
from app.db.models.recurrence import Recurrence
from app.db.models.relationships import meeting_users
from app.db.models.user import User
from app.db.repositories import BaseRepository


class MeetingRepository(BaseRepository[Meeting]):
    def __init__(self, db: AsyncSession):
        super().__init__(Meeting, db)

    async def filter_meetings(
        self,
        filters: dict[str, Any],
        after_date: datetime,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Meeting]:
        logger.debug(
            f"Filtering meetings with filters={filters}, after_date={after_date}"
        )

        stmt = select(self.model)
        for field, value in filters.items():
            stmt = stmt.filter(getattr(self.model, field) == value)

        if after_date:
            stmt = stmt.filter(self.model.start_date > after_date)

        stmt = stmt.order_by(self.model.start_date).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        meetings = list(result.scalars().all())

        logger.debug(f"Retrieved {len(meetings)} meetings with filters={filters}")
        return meetings

    async def get_recurrence_by_id(self, recurrence_id: int) -> Optional[Recurrence]:
        logger.debug(f"Fetching recurrence with ID: {recurrence_id}")

        stmt = select(Recurrence).where(Recurrence.id == recurrence_id)
        result = await self.db.execute(stmt)
        recurrence = result.scalar_one_or_none()

        if not recurrence:
            logger.warning(f"Recurrence with ID {recurrence_id} not found")
        else:
            logger.debug(f"Recurrence retrieved: {recurrence}")

        return recurrence

    async def get_future_meetings(
        self, recurrence_id: int, after_date: datetime, skip: int = 0, limit: int = 10
    ) -> list[Meeting]:
        meetings = await self.filter_meetings(
            filters={"recurrence_id": recurrence_id},
            after_date=after_date,
            skip=skip,
            limit=limit,
        )
        return list(meetings)

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
        meetings = list(result.scalars().unique().all())
        logger.debug(f"Retrieved {len(meetings)} meetings for user ID {user_id}")
        return meetings

    async def add_users_to_meeting(self, meeting_id: int, user_ids: list[UUID]) -> None:
        logger.info(f"Adding users to meeting ID {meeting_id}: {user_ids}")

        # Fetch existing user-meeting relationships in bulk
        stmt = select(meeting_users).where(
            meeting_users.c.meeting_id == meeting_id,
            meeting_users.c.user_id.in_(user_ids),
        )
        result = await self.db.execute(stmt)
        existing_users = {user_id for (user_id,) in result}

        # Determine which users need to be added
        new_user_ids = [
            user_id for user_id in user_ids if user_id not in existing_users
        ]

        if not new_user_ids:
            logger.info(f"All users are already added to meeting ID {meeting_id}")
            return

        # Perform a batch insert for new relationships
        values = [
            {"meeting_id": meeting_id, "user_id": user_id} for user_id in new_user_ids
        ]
        insert_stmt = meeting_users.insert().values(values)

        try:
            await self.db.execute(insert_stmt)
            await self.db.commit()
            logger.info(
                f"Successfully added users to meeting ID {meeting_id}: {new_user_ids}"
            )
        except Exception as e:
            logger.exception(f"Error adding users to meeting ID {meeting_id}: {e}")
            raise

    async def get_users_from_meeting(self, meeting_id: int) -> list[User]:
        logger.info(f"Fetching users for meeting ID {meeting_id}")

        try:
            # Join meeting_users with users to fetch user details
            stmt = (
                select(User)
                .join(meeting_users, User.id == meeting_users.c.user_id)
                .where(meeting_users.c.meeting_id == meeting_id)
            )

            result = await self.db.execute(stmt)
            users = list(result.scalars().all())
            logger.info(f"Found {len(users)} users for meeting ID {meeting_id}")
            return users
        except Exception as e:
            logger.exception(f"Error fetching users for meeting ID {meeting_id}: {e}")
            raise

    async def complete_meeting(self, meeting_id: int) -> Optional[Meeting]:
        logger.debug(f"Marking meeting with ID {meeting_id} as complete")
        meeting = await self.get_by_id(meeting_id)
        if meeting:
            await self.db.execute(
                update(Meeting).where(Meeting.id == meeting.id).values(completed=True)
            )
            await self.db.commit()
            await self.db.refresh(meeting)
            logger.debug(f"Meeting with ID {meeting_id} marked as complete")
        else:
            logger.warning(f"Meeting with ID {meeting_id} not found")
        return meeting

    async def batch_create_with_recurrence(
        self, recurrence_id: int, base_meeting: dict[str, Any], dates: list[datetime]
    ) -> dict[str, list[Meeting] | list[datetime]]:
        if not dates:
            logger.warning("No dates provided for batch creation.")
            raise ValueError("Dates list cannot be empty.")

        # Validate recurrence
        recurrence = await self.db.get(Recurrence, recurrence_id)
        if not recurrence:
            logger.warning(f"Recurrence with ID {recurrence_id} not found.")
            raise ValueError(f"Recurrence with ID {recurrence_id} does not exist.")

        # Check for duplicate dates
        existing_meetings = await self.filter_meetings(
            filters={"recurrence_id": recurrence_id},
            after_date=min(dates),
        )
        existing_dates = {meeting.start_date for meeting in existing_meetings}
        unique_dates = [date for date in dates if date not in existing_dates]

        if not unique_dates:
            logger.info("All provided dates are duplicates; no meetings created.")
            return {"created_meetings": [], "skipped_dates": dates}

        # Prepare and insert meetings
        meetings = [
            self.model(
                recurrence_id=recurrence_id,
                start_date=start_date,
                **{k: v for k, v in base_meeting.items() if k not in ["start_date"]},
            )
            for start_date in unique_dates
        ]

        try:
            self.db.add_all(meetings)
            await self.db.commit()
            logger.debug(
                f"Created {len(meetings)} meetings for recurrence ID {recurrence_id}"
            )
        except Exception as e:
            logger.error(f"Error during batch creation: {e}")
            await self.db.rollback()
            raise

        return {
            "created_meetings": meetings,
            "skipped_dates": [date for date in dates if date in existing_dates],
        }
