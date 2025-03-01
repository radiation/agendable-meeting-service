from datetime import datetime, timedelta
from typing import Optional, cast
from uuid import UUID

from app.core.logging_config import logger
from app.core.redis_client import RedisClient
from app.db.models.meeting import Meeting
from app.db.repositories.meeting_repo import MeetingRepository
from app.exceptions import NotFoundError, ValidationError
from app.schemas.meeting_schemas import MeetingCreate, MeetingRetrieve, MeetingUpdate
from app.schemas.user_schemas import UserRetrieve
from app.services import BaseService


class MeetingService(BaseService[Meeting, MeetingCreate, MeetingUpdate]):
    def __init__(
        self, repo: MeetingRepository, redis_client: Optional[RedisClient] = None
    ) -> None:
        super().__init__(repo, redis_client=redis_client)
        self.repo: MeetingRepository = repo

    async def get_meeting_attendees(self, meeting_id: int) -> list[UserRetrieve]:
        logger.info(f"Fetching attendees for meeting ID {meeting_id}")
        attendees = await self.repo.get_users_from_meeting(meeting_id)
        logger.info(f"Retrieved {len(attendees)} attendees for meeting ID {meeting_id}")
        return [UserRetrieve.model_validate(user) for user in attendees]

    async def get_meetings_by_user_id(
        self, user_id: UUID, skip: int = 0, limit: int = 10
    ) -> list[MeetingRetrieve]:
        logger.info(f"Fetching meetings for user with ID: {user_id}")
        meetings = await self.repo.get_meetings_by_user_id(user_id, skip, limit)
        logger.info(f"Retrieved {len(meetings)} meetings for user with ID: {user_id}")
        return [MeetingRetrieve.model_validate(meeting) for meeting in meetings]

    async def complete_meeting(self, meeting_id: int) -> MeetingRetrieve:
        logger.info(f"Completing meeting with ID: {meeting_id}")
        meeting = await self.repo.get_by_id(meeting_id)
        if not meeting:
            logger.warning(f"Meeting with ID {meeting_id} not found")
            raise NotFoundError(detail=f"Meeting with ID {meeting_id} not found")

        # Get the next meeting in the recurrence
        next_meeting = await self.get_subsequent_meeting(meeting_id)
        next_meeting_id = next_meeting.id if next_meeting else None

        # Publish event with both source and target meeting IDs
        await self._publish_event(
            event_type="complete",
            payload={
                "meeting_id": meeting_id,
                "next_meeting_id": next_meeting_id,
            },
        )

        # Mark meeting as complete
        meeting.completed = cast(bool, True)
        meeting = await self.repo.update(meeting)
        logger.info(f"Successfully completed meeting with ID: {meeting_id}")

        return MeetingRetrieve.model_validate(meeting)

    async def get_subsequent_meeting(self, meeting_id: int) -> MeetingRetrieve:
        logger.info(f"Fetching subsequent meeting for meeting with ID: {meeting_id}")

        # Fetch meeting and validate
        meeting = await self.repo.get_by_id(meeting_id)
        if not meeting:
            logger.warning(f"Meeting with ID {meeting_id} not found")
            raise NotFoundError(detail=f"Meeting with ID {meeting_id} not found")

        if not meeting.recurrence_id:
            logger.warning(f"Meeting {meeting_id} does not have a recurrence set")
            raise ValidationError(
                detail=f"Meeting {meeting_id} does not have a recurrence set"
            )

        after_date = cast(datetime, meeting.start_date) + timedelta(
            minutes=cast(float, meeting.duration)
        )

        # Fetch subsequent meetings
        recurrence_id = cast(int, meeting.recurrence_id)
        next_meeting = await self.repo.get_future_meetings(
            recurrence_id=recurrence_id, after_date=after_date
        )

        if not next_meeting:
            logger.info("Creating subsequent meeting")
            return await self.create_subsequent_meeting(meeting)

        logger.info(f"Found subsequent meeting with ID: {next_meeting[0].id}")
        return MeetingRetrieve.model_validate(next_meeting[0])

    async def create_subsequent_meeting(self, meeting: Meeting) -> MeetingRetrieve:
        logger.info(f"Creating subsequent meeting for meeting with ID: {meeting.id}")

        if not meeting.recurrence_id:
            logger.warning(
                f"Meeting with ID {meeting.id} does not have a recurrence set"
            )
            raise ValidationError(
                detail=f"Meeting with ID {meeting.id} does not have a recurrence set"
            )

        # Fetch recurrence and generate next date
        recurrence_id = cast(int, meeting.recurrence_id)
        recurrence = await self.repo.get_recurrence_by_id(recurrence_id)
        if not recurrence:
            logger.warning(f"Recurrence with ID {recurrence_id} not found")
            raise NotFoundError(detail=f"Recurrence with ID {recurrence_id} not found")

        start_date = cast(datetime, meeting.start_date)
        next_meeting_date = recurrence.get_next_date(start_date=start_date)

        if not next_meeting_date:
            logger.warning("No future dates found in the recurrence rule")
            raise ValidationError(detail="No future dates found in the recurrence rule")

        # Create new meeting
        meeting_data = Meeting(
            title=meeting.title,
            start_date=next_meeting_date,
            duration=meeting.duration,
            location=meeting.location,
            notes=meeting.notes,
            recurrence_id=meeting.recurrence_id,
        )
        new_meeting = await self.repo.create(meeting_data)
        if not new_meeting:
            logger.warning("Failed to create subsequent meeting")
            raise ValidationError(detail="Failed to create subsequent meeting")
        logger.info(
            f"Successfully created subsequent meeting with ID: {new_meeting.id}"
        )

        return MeetingRetrieve.model_validate(new_meeting)

    async def create_recurring_meetings(
        self, recurrence_id: int, base_meeting: MeetingCreate, dates: list[datetime]
    ) -> list[MeetingRetrieve]:
        logger.info(
            f"Creating recurring meetings for recurrence with ID: {recurrence_id}"
        )

        # Validate recurrence
        recurrence = await self.repo.get_recurrence_by_id(recurrence_id)
        if not recurrence:
            logger.warning(f"Recurrence with ID {recurrence_id} not found")
            raise NotFoundError(detail=f"Recurrence with ID {recurrence_id} not found")

        meetings = await self.repo.batch_create_with_recurrence(
            recurrence_id, base_meeting, dates
        )
        if not meetings:
            logger.warning("No meetings created")
            raise ValidationError(detail="No meetings created")

        return [MeetingRetrieve.model_validate(meeting) for meeting in meetings]

    async def add_users(self, meeting_id: int, user_ids: list[UUID]) -> None:
        logger.info(f"Adding users to meeting ID {meeting_id}: {user_ids}")

        # Ensure the meeting exists
        meeting = await self.repo.get_by_id(meeting_id)
        if not meeting:
            logger.warning(f"Meeting with ID {meeting_id} not found")
            raise NotFoundError(detail=f"Meeting with ID {meeting_id} not found")

        await self.repo.add_users_to_meeting(meeting_id, user_ids)
        logger.info(f"Successfully added users to meeting ID {meeting_id}")

    async def get_users(self, meeting_id: int) -> list[UserRetrieve]:
        logger.info(f"Retrieving users for meeting ID {meeting_id}")

        meeting = await self.repo.get_by_id(meeting_id)
        if not meeting:
            logger.warning(f"Meeting with ID {meeting_id} not found")
            raise NotFoundError(detail=f"Meeting with ID {meeting_id} not found")

        users = await self.repo.get_users_from_meeting(meeting_id)
        logger.info(f"Retrieved {len(users)} users for meeting ID {meeting_id}")
        return [UserRetrieve.model_validate(user) for user in users]
