from datetime import datetime

from app.db.models import Meeting, MeetingRecurrence
from app.db.repositories.meeting_attendee_repo import MeetingAttendeeRepository
from app.db.repositories.meeting_repo import MeetingRepository
from app.exceptions import NotFoundError, ValidationError
from app.schemas.meeting_schemas import MeetingCreate, MeetingRetrieve, MeetingUpdate
from app.services.base_service import BaseService
from dateutil.rrule import rrulestr


class MeetingService(BaseService[Meeting, MeetingCreate, MeetingUpdate]):
    def __init__(
        self, repo: MeetingRepository, attendee_repo: MeetingAttendeeRepository
    ):
        self.repo = repo
        self.attendee_repo = attendee_repo

    async def create_meeting_with_recurrence(
        self, meeting_data: MeetingCreate
    ) -> MeetingRetrieve:
        if meeting_data.recurrence_id:
            recurrence = await self.repo.db.get(
                MeetingRecurrence, meeting_data.recurrence_id
            )
            if not recurrence:
                raise ValidationError(
                    detail=f"Recurrence with ID {meeting_data.recurrence_id} not found"
                )

        meeting = await self.repo.create_with_recurrence(meeting_data.model_dump())
        return MeetingRetrieve.model_validate(meeting)

    async def complete_meeting(self, meeting_id: int) -> MeetingRetrieve:
        meeting = await self.repo.get_by_id_with_recurrence(meeting_id)
        if not meeting:
            raise NotFoundError(detail=f"Meeting with ID {meeting_id} not found")

        meeting.completed = True
        await self.repo.db.commit()
        await self.repo.db.refresh(meeting)
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
        meeting = await self.repo.get_by_id_with_recurrence(meeting_id)
        if not meeting:
            raise NotFoundError(detail=f"Meeting with ID {meeting_id} not found")

        if not meeting.recurrence_id:
            raise ValidationError(
                detail=f"Meeting {meeting_id} does not have a recurrence set"
            )

        recurrence = await self.repo.db.get(MeetingRecurrence, meeting.recurrence_id)
        if not recurrence:
            raise NotFoundError(
                detail=f"Recurrence with ID {meeting.recurrence_id} not found"
            )

        next_meeting = await self.repo.get_meetings_with_recurrence(
            recurrence_id=meeting.recurrence_id, after_date=after_date
        )

        if not next_meeting:
            next_meeting = await self.create_subsequent_meeting(meeting)
        else:
            next_meeting = next_meeting[0]

        return MeetingRetrieve.model_validate(next_meeting)

    async def create_subsequent_meeting(self, meeting: Meeting) -> MeetingRetrieve:
        if not meeting:
            raise NotFoundError(detail="Meeting not found")

        if not meeting.recurrence_id:
            raise ValidationError(
                detail=f"Meeting with ID {meeting.id} does not have a recurrence set"
            )

        recurrence = await self.repo.db.get(MeetingRecurrence, meeting.recurrence_id)
        if not recurrence:
            raise NotFoundError(
                detail=f"Recurrence with ID {meeting.recurrence_id} not found"
            )

        try:
            rule = rrulestr(recurrence.rrule, dtstart=meeting.start_date)
            next_meeting_date = rule.after(meeting.start_date, inc=False)
        except Exception as e:
            raise ValidationError(detail=f"Error parsing recurrence rule: {str(e)}")

        if not next_meeting_date:
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

        new_meeting = await self.repo.create(meeting_data.model_dump())
        return MeetingRetrieve.model_validate(new_meeting)

    async def create_meeting_with_recurrence_and_attendees(
        self, meeting_data: dict, attendees: list[dict]
    ):
        async with self.repo.db.begin():
            meeting = await self.repo.create_with_recurrence(meeting_data)

            for attendee_data in attendees:
                attendee_data["meeting_id"] = meeting.id
                await self.attendee_repo.create(attendee_data)

            return meeting

    async def create_recurring_meetings(
        self, recurrence_id: int, base_meeting: dict, dates: list[datetime]
    ):
        recurrence = await self.repo.db.get(MeetingRecurrence, recurrence_id)
        if not recurrence:
            raise NotFoundError(detail=f"Recurrence with ID {recurrence_id} not found")

        meetings = await self.repo.batch_create_with_recurrence(
            recurrence_id, base_meeting, dates
        )
        return [meeting.model_dump() for meeting in meetings]
