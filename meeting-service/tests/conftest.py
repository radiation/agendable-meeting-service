import pytest
from app.db.db import get_db
from app.db.models import Base
from app.db.repositories import (
    MeetingRepository,
    RecurrenceRepository,
    TaskRepository,
    UserRepository,
)
from app.main import app
from app.services import MeetingService, RecurrenceService, TaskService, UserService
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

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest.fixture
async def meeting_service(db_session):
    repo = MeetingRepository(db_session)
    service = MeetingService(repo=repo)
    return service


@pytest.fixture
async def recurrence_service(db_session):
    repo = RecurrenceRepository(db_session)
    service = RecurrenceService(repo)
    return service


@pytest.fixture
async def task_service(db_session):
    repo = TaskRepository(db_session)
    service = TaskService(repo)
    return service


@pytest.fixture
async def user_service(db_session):
    repo = UserRepository(db_session)
    service = UserService(repo)
    return service
