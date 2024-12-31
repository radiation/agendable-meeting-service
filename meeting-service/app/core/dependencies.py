from app.db.db import get_db
from app.db.repositories.meeting_attendee_repo import MeetingAttendeeRepository
from app.db.repositories.meeting_recurrence_repo import MeetingRecurrenceRepository
from app.db.repositories.meeting_repo import MeetingRepository
from app.db.repositories.meeting_task_repo import MeetingTaskRepository
from app.db.repositories.task_repo import TaskRepository
from app.services.meeting_attendee_service import MeetingAttendeeService
from app.services.meeting_recurrence_service import MeetingRecurrenceService
from app.services.meeting_service import MeetingService
from app.services.meeting_task_service import MeetingTaskService
from app.services.task_service import TaskService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_meeting_repo(db: AsyncSession = Depends(get_db)) -> MeetingRepository:
    return MeetingRepository(db)


def get_meeting_service(db: AsyncSession = Depends(get_db)) -> MeetingService:
    meeting_repo = MeetingRepository(db)
    attendee_repo = MeetingAttendeeRepository(db)
    return MeetingService(meeting_repo, attendee_repo)


def get_meeting_attendee_repo(
    db: AsyncSession = Depends(get_db),
) -> MeetingAttendeeRepository:
    return MeetingAttendeeRepository(db)


def get_meeting_attendee_service(
    db: AsyncSession = Depends(get_db),
) -> MeetingAttendeeService:
    attendee_repo = MeetingAttendeeRepository(db)
    return MeetingAttendeeService(attendee_repo)


def get_meeting_recurrence_repo(
    db: AsyncSession = Depends(get_db),
) -> MeetingRecurrenceRepository:
    return MeetingRecurrenceRepository(db)


def get_meeting_recurrence_service(
    db: AsyncSession = Depends(get_db),
) -> MeetingRecurrenceService:
    recurrence_repo = MeetingRecurrenceRepository(db)
    return MeetingRecurrenceService(recurrence_repo)


def get_meeting_task_repo(
    db: AsyncSession = Depends(get_db),
) -> MeetingTaskRepository:
    return MeetingTaskRepository(db)


def get_meeting_task_service(db: AsyncSession = Depends(get_db)) -> MeetingTaskService:
    task_repo = MeetingTaskRepository(db)
    return MeetingTaskService(task_repo)


def get_task_repo(db: AsyncSession = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)


def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    task_repo = TaskRepository(db)
    return TaskService(task_repo)
