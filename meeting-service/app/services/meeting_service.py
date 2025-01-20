from datetime import datetime
from uuid import UUID

from app.core.logging_config import logger
from app.db.models import Meeting, Recurrence
from app.db.repositories import MeetingRepository
from app.exceptions import NotFoundError, ValidationError
from app.schemas import MeetingCreate, MeetingRetrieve, MeetingUpdate
from app.services import BaseService
from dateutil.rrule import rrulestr


class MeetingService(BaseService[Meeting, MeetingCreate, MeetingUpdate]):
    def __init__(
        self,
        repo: MeetingRepository,
        redis_client=None,
    ):
        super().__init__(repo, model_name="Meeting", redis_client=redis_client)

    async def create_meeting_with_recurrence(
        self, meeting_data: MeetingCreate
    ) -> MeetingRetrieve:
        logger.info(
            f"Starting create_meeting_with_recurrence \
                with data: {meeting_data.model_dump()}"
        )
        if meeting_data.recurrence_id:
            recurrence = await self.repo.db.get(Recurrence, meeting_data.recurrence_id)
            if not recurrence:
                logger.warning(
                    f"Recurrence with ID {meeting_data.recurrence_id} not found"
                )
                raise ValidationError(
                    detail=f"Recurrence with ID {meeting_data.recurrence_id} not found"
                )

        meeting = await self.repo.create_with_recurrence(meeting_data.model_dump())
        logger.info(f"Successfully created meeting with ID: {meeting.id}")
        return MeetingRetrieve.model_validate(meeting)

    async def get_meetings_by_user_id(
        self, user_id: int, skip: int = 0, limit: int = 10
    ) -> list[MeetingRetrieve]:
        logger.info(f"Fetching meetings for user with ID: {user_id}")
        meetings = await self.repo.get_meetings_by_user_id(user_id, skip, limit)
        logger.info(f"Retrieved {len(meetings)} meetings for user with ID: {user_id}")
        return [MeetingRetrieve.model_validate(meeting) for meeting in meetings]

    async def complete_meeting(self, meeting_id: int) -> MeetingRetrieve:
        logger.info(f"Completing meeting with ID: {meeting_id}")
        meeting = await self.repo.get_by_id_with_recurrence(meeting_id)
        if not meeting:
            logger.warning(f"Meeting with ID {meeting_id} not found")
            raise NotFoundError(detail=f"Meeting with ID {meeting_id} not found")

        meeting.completed = True
        await self.repo.db.commit()
        await self.repo.db.refresh(meeting)
        logger.info(f"Successfully completed meeting with ID: {meeting_id}")
        return MeetingRetrieve.model_validate(meeting)

    async def add_recurrence(
        self, meeting_id: int, recurrence_id: int
    ) -> MeetingRetrieve:
        meeting = await self.repo.get_by_id_with_recurrence(meeting_id)
        if not meeting:
            raise NotFoundError(detail=f"Meeting with ID {meeting_id} not found")

        meeting.recurrence_id = recurrence_id
        await self.repo.db.commit()
        await self.repo.db.refresh(meeting)
        return MeetingRetrieve.model_validate(meeting)

    async def get_subsequent_meeting(
        self, meeting_id: int, after_date: datetime = datetime.now()
    ) -> MeetingRetrieve:
        logger.info(f"Fetching subsequent meeting for meeting with ID: {meeting_id}")
        meeting = await self.repo.get_by_id_with_recurrence(meeting_id)
        if not meeting:
            logger.warning(f"Meeting with ID {meeting_id} not found")
            raise NotFoundError(detail=f"Meeting with ID {meeting_id} not found")

        if not meeting.recurrence_id:
            logger.warning(f"Meeting {meeting_id} does not have a recurrence set")
            raise ValidationError(
                detail=f"Meeting {meeting_id} does not have a recurrence set"
            )

        recurrence = await self.repo.db.get(Recurrence, meeting.recurrence_id)
        if not recurrence:
            logger.warning(f"Recurrence with ID {meeting.recurrence_id} not found")
            raise NotFoundError(
                detail=f"Recurrence with ID {meeting.recurrence_id} not found"
            )

        next_meeting = await self.repo.get_meetings_with_recurrence(
            recurrence_id=meeting.recurrence_id, after_date=after_date
        )

        if not next_meeting:
            logger.info("Creating subsequent meeting")
            next_meeting = await self.create_subsequent_meeting(meeting)
        else:
            logger.info(f"Found subsequent meeting with ID: {next_meeting[0].id}")
            next_meeting = next_meeting[0]

        return MeetingRetrieve.model_validate(next_meeting)

    async def create_subsequent_meeting(self, meeting: Meeting) -> MeetingRetrieve:
        logger.info(f"Creating subsequent meeting for meeting with ID: {meeting.id}")
        if not meeting:
            logger.warning(f"Meeting with ID {meeting.id} not found")
            raise NotFoundError(detail="Meeting not found")

        if not meeting.recurrence_id:
            logger.warning(
                f"Meeting with ID {meeting.id} does not have a recurrence set"
            )
            raise ValidationError(
                detail=f"Meeting with ID {meeting.id} does not have a recurrence set"
            )

        recurrence = await self.repo.db.get(Recurrence, meeting.recurrence_id)
        if not recurrence:
            logger.warning(f"Recurrence with ID {meeting.recurrence_id} not found")
            raise NotFoundError(
                detail=f"Recurrence with ID {meeting.recurrence_id} not found"
            )

        try:
            rule = rrulestr(recurrence.rrule, dtstart=meeting.start_date)
            next_meeting_date = rule.after(meeting.start_date, inc=False)
            logger.info(f"Next meeting date: {next_meeting_date}")
        except Exception as e:
            logger.error(f"Error parsing recurrence rule: {str(e)}")
            raise ValidationError(detail=f"Error parsing recurrence rule: {str(e)}")

        if not next_meeting_date:
            logger.warning("No future dates found in the recurrence rule")
            raise ValidationError(detail="No future dates found in the recurrence rule")

        duration = meeting.end_date - meeting.start_date if meeting.end_date else None
        next_meeting_end_date = next_meeting_date + duration if duration else None

        meeting_data = MeetingCreate(
            title=meeting.title,
            start_date=next_meeting_date,
            end_date=next_meeting_end_date,
            duration=meeting.duration,
            location=meeting.location,
            notes=meeting.notes,
            recurrence_id=meeting.recurrence_id,
        )

        logger.info(
            f"Creating subsequent meeting with data: {meeting_data.model_dump()}"
        )
        new_meeting = await self.repo.create(meeting_data.model_dump())
        logger.info(
            f"Successfully created subsequent meeting with ID: {new_meeting.id}"
        )
        return MeetingRetrieve.model_validate(new_meeting)

    async def create_recurring_meetings(
        self, recurrence_id: int, base_meeting: dict, dates: list[datetime]
    ):
        logger.info(
            f"Creating recurring meetings for recurrence with ID: {recurrence_id}"
        )
        recurrence = await self.repo.db.get(Recurrence, recurrence_id)
        if not recurrence:
            logger.warning(f"Recurrence with ID {recurrence_id} not found")
            raise NotFoundError(detail=f"Recurrence with ID {recurrence_id} not found")

        meetings = await self.repo.batch_create_with_recurrence(
            recurrence_id, base_meeting, dates
        )
        if not meetings:
            logger.warning("No meetings created")
            raise ValidationError(detail="No meetings created")
        return [meeting.model_dump() for meeting in meetings]

    async def add_users(self, meeting_id: int, user_ids: list[UUID]):
        logger.info(f"Adding users to meeting ID {meeting_id}: {user_ids}")

        # Ensure the meeting exists
        meeting = await self.repo.get_by_id(meeting_id)
        if not meeting:
            logger.warning(f"Meeting with ID {meeting_id} not found")
            raise NotFoundError(detail=f"Meeting with ID {meeting_id} not found")

        await self.repo.add_users_to_meeting(meeting_id, user_ids)
        logger.info(f"Successfully added users to meeting ID {meeting_id}")

    async def get_users(self, meeting_id: int):
        logger.info(f"Retrieving users for meeting ID {meeting_id}")

        meeting = await self.repo.get_by_id(meeting_id)
        if not meeting:
            logger.warning(f"Meeting with ID {meeting_id} not found")
            raise NotFoundError(detail=f"Meeting with ID {meeting_id} not found")

        return await self.repo.get_users_from_meeting(meeting_id)
