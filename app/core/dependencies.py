from app.core.redis_client import redis_client
from app.db.db import get_db
from app.db.repositories import (
    MeetingRepository,
    RecurrenceRepository,
    TaskRepository,
    UserRepository,
)
from app.services import MeetingService, RecurrenceService, TaskService, UserService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def get_redis_client():
    return redis_client


def get_meeting_repo(db: AsyncSession = Depends(get_db)) -> MeetingRepository:
    return MeetingRepository(db)


def get_meeting_service(
    db: AsyncSession = Depends(get_db), redis=Depends(lambda: redis_client)
) -> MeetingService:
    meeting_repo = MeetingRepository(db)
    return MeetingService(meeting_repo, redis_client=redis)


def get_recurrence_repo(
    db: AsyncSession = Depends(get_db),
) -> RecurrenceRepository:
    return RecurrenceRepository(db)


def get_recurrence_service(
    db: AsyncSession = Depends(get_db), redis=Depends(lambda: redis_client)
) -> RecurrenceService:
    recurrence_repo = RecurrenceRepository(db)
    return RecurrenceService(recurrence_repo, redis_client=redis)


def get_task_repo(db: AsyncSession = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)


def get_task_service(
    db: AsyncSession = Depends(get_db), redis=Depends(lambda: redis_client)
) -> TaskService:
    task_repo = TaskRepository(db)
    return TaskService(task_repo, redis_client=redis)


def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(
    db: AsyncSession = Depends(get_db), redis=Depends(lambda: redis_client)
) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo, redis_client=redis)
