from fastapi import Depends
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import redis_client
from app.db.db import get_db
from app.db.repositories.meeting_repo import MeetingRepository
from app.db.repositories.recurrence_repo import RecurrenceRepository
from app.db.repositories.task_repo import TaskRepository
from app.db.repositories.user_repo import UserRepository
from app.services.meeting_service import MeetingService
from app.services.recurrence_service import RecurrenceService
from app.services.task_service import TaskService
from app.services.user_service import UserService

__all__ = ["get_db", "get_redis_client", "get_task_service", "get_user_service"]


def get_redis_client() -> Redis:
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
