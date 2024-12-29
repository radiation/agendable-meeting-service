import pytest
from app.api.routers.meeting_router import get_attendee
from app.db.db import get_db
from app.main import app
from app.models import Base
from app.repositories.meeting_attendee_repository import MeetingAttendeeRepository
from app.repositories.meeting_recurrence_repository import MeetingRecurrenceRepository
from app.repositories.meeting_repository import MeetingRepository
from app.repositories.meeting_task_repository import MeetingTaskRepository
from app.repositories.task_repository import TaskRepository
from app.services.meeting_attendee_service import MeetingAttendeeService
from app.services.meeting_recurrence_service import MeetingRecurrenceService
from app.services.meeting_service import MeetingService
from app.services.meeting_task_service import MeetingTaskService
from app.services.task_service import TaskService
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
async def engine():
    # Create an in-memory SQLite engine
    _engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield _engine
    await _engine.dispose()


@pytest.fixture(scope="session")
async def tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session():
    # Create an isolated in-memory SQLite database for each test
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        yield session

    # Dispose of the engine after the test
    await engine.dispose()


@pytest.fixture
async def test_client(db_session):
    # Override the get_db dependency
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_attendee] = lambda: {"private_notes": "Mock notes"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest.fixture
async def meeting_service(db_session):
    repo = MeetingRepository(db_session)
    service = MeetingService(repository=repo, attendee_repo=None)
    return service


@pytest.fixture
async def meeting_attendee_service(db_session):
    repo = MeetingAttendeeRepository(db_session)
    service = MeetingAttendeeService(repo)
    return service


@pytest.fixture
async def meeting_recurrence_service(db_session):
    repo = MeetingRecurrenceRepository(db_session)
    service = MeetingRecurrenceService(repo)
    return service


@pytest.fixture
async def task_service(db_session):
    repo = TaskRepository(db_session)
    service = TaskService(repo)
    return service


@pytest.fixture
async def meeting_task_service(db_session):
    repo = MeetingTaskRepository(db_session)
    service = MeetingTaskService(repo)
    return service
