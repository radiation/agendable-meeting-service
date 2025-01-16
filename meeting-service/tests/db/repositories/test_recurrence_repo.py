import pytest
from app.db.models import Recurrence
from app.db.repositories import RecurrenceRepository


@pytest.mark.asyncio
async def test_create_recurrence(db_session):
    repo = RecurrenceRepository(db_session)

    new_recurrence = {
        "title": "Test Recurrence",
        "rrule": "FREQ=DAILY;INTERVAL=1",
    }
    recurrence = await repo.create(new_recurrence)
    assert recurrence.title == "Test Recurrence"
    assert recurrence.rrule == "FREQ=DAILY;INTERVAL=1"


@pytest.mark.asyncio
async def test_get_recurrence(db_session):
    repo = RecurrenceRepository(db_session)

    # Create a test recurrence
    recurrence = Recurrence(title="Test Recurrence", rrule="FREQ=DAILY;INTERVAL=1")
    db_session.add(recurrence)
    await db_session.commit()

    # Fetch the recurrence
    retrieved = await repo.get_by_id(recurrence.id)
    assert retrieved.id == recurrence.id
    assert retrieved.title == "Test Recurrence"


@pytest.mark.asyncio
async def test_delete_recurrence(db_session):
    repo = RecurrenceRepository(db_session)

    # Create a test recurrence
    recurrence = Recurrence(title="Test Recurrence", rrule="FREQ=DAILY;INTERVAL=1")
    db_session.add(recurrence)
    await db_session.commit()

    # Delete the recurrence
    await repo.delete(recurrence.id)
    deleted = await repo.get_by_id(recurrence.id)
    assert deleted is None
