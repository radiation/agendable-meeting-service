"""
Fixtures for testing the FastAPI application
"""

from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.dependencies import (
    get_meeting_service,
    get_recurrence_service,
    get_task_service,
    get_user_service,
)
from app.db.db import get_db
from app.db.models import Base
from app.db.repositories.meeting_repo import MeetingRepository
from app.db.repositories.recurrence_repo import RecurrenceRepository
from app.db.repositories.task_repo import TaskRepository
from app.db.repositories.user_repo import UserRepository
from app.main import app
from app.services.meeting_service import MeetingService
from app.services.recurrence_service import RecurrenceService
from app.services.task_service import TaskService
from app.services.user_service import UserService

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(name="engine", scope="session")
async def _engine():
    """Create a new test database for the entire test session"""
    _engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield _engine
    await _engine.dispose()


@pytest.fixture(scope="session")
async def tables(engine):
    """Create tables for the test database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(name="db_session", scope="function")
async def _db_session(engine):
    """Create a new test session for each test function"""
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture(name="mock_redis_client")
async def _mock_redis_client():
    """Mock Redis client for testing"""
    mock = AsyncMock()
    mock.publish = AsyncMock()
    return mock


@pytest.fixture
async def test_client(db_session, mock_redis_client):
    """Test client with dependency overrides for services"""
    app.dependency_overrides[get_db] = lambda: db_session

    app.dependency_overrides[get_meeting_service] = lambda: MeetingService(
        MeetingRepository(db_session), mock_redis_client
    )

    app.dependency_overrides[get_recurrence_service] = lambda: RecurrenceService(
        RecurrenceRepository(db_session), mock_redis_client
    )

    app.dependency_overrides[get_task_service] = lambda: TaskService(
        TaskRepository(db_session), mock_redis_client
    )

    app.dependency_overrides[get_user_service] = lambda: UserService(
        UserRepository(db_session), mock_redis_client
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest.fixture
async def meeting_service(db_session, mock_redis_client):
    """Create a new MeetingService instance for each test function"""
    repo = MeetingRepository(db_session)
    service = MeetingService(repo, mock_redis_client)
    return service


@pytest.fixture
async def recurrence_service(db_session, mock_redis_client):
    """Create a new RecurrenceService instance for each test function"""
    repo = RecurrenceRepository(db_session)
    service = RecurrenceService(repo, mock_redis_client)
    return service


@pytest.fixture
async def task_service(db_session, mock_redis_client):
    """Create a new TaskService instance for each test function"""
    repo = TaskRepository(db_session)
    service = TaskService(repo, mock_redis_client)
    return service


@pytest.fixture
async def user_service(db_session, mock_redis_client):
    """Create a new UserService instance for each test function"""
    repo = UserRepository(db_session)
    service = UserService(repo, mock_redis_client)
    return service
