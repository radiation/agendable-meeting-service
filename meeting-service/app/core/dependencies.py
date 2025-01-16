from app.db.db import get_db
from app.db.repositories.attendee_repo import AttendeeRepository
from app.db.repositories.meeting_repo import MeetingRepository
from app.db.repositories.recurrence_repo import RecurrenceRepository
from app.db.repositories.task_repo import TaskRepository
from app.services.attendee_service import AttendeeService
from app.services.meeting_service import MeetingService
from app.services.recurrence_service import RecurrenceService
from app.services.task_service import TaskService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_meeting_repo(db: AsyncSession = Depends(get_db)) -> MeetingRepository:
    return MeetingRepository(db)


def get_meeting_service(db: AsyncSession = Depends(get_db)) -> MeetingService:
    meeting_repo = MeetingRepository(db)
    attendee_repo = AttendeeRepository(db)
    return MeetingService(meeting_repo, attendee_repo)


def get_attendee_repo(
    db: AsyncSession = Depends(get_db),
) -> AttendeeRepository:
    return AttendeeRepository(db)


def get_attendee_service(
    db: AsyncSession = Depends(get_db),
) -> AttendeeService:
    attendee_repo = AttendeeRepository(db)
    return AttendeeService(attendee_repo)


def get_recurrence_repo(
    db: AsyncSession = Depends(get_db),
) -> RecurrenceRepository:
    return RecurrenceRepository(db)


def get_recurrence_service(
    db: AsyncSession = Depends(get_db),
) -> RecurrenceService:
    recurrence_repo = RecurrenceRepository(db)
    return RecurrenceService(recurrence_repo)


def get_task_repo(db: AsyncSession = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)


def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    task_repo = TaskRepository(db)
    return TaskService(task_repo)
