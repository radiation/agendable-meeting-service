import pytest
from app.db.models import Recurrence
from app.db.repositories import RecurrenceRepository
from app.schemas import RecurrenceCreate, RecurrenceUpdate


@pytest.mark.asyncio
async def test_create_recurrence_service(recurrence_service, db_session):
    new_recurrence = RecurrenceCreate(
        title="Service Test Recurrence", rrule="FREQ=DAILY;INTERVAL=1"
    )
    created = await recurrence_service.create(new_recurrence)
    assert created.title == "Service Test Recurrence"
    assert created.rrule == "FREQ=DAILY;INTERVAL=1"


@pytest.mark.asyncio
async def test_get_recurrence_service(recurrence_service, db_session):
    recurrence = Recurrence(title="Test Recurrence", rrule="FREQ=DAILY;INTERVAL=1")
    db_session.add(recurrence)
    await db_session.commit()

    retrieved = await recurrence_service.get_by_id(recurrence.id)
    assert retrieved.id == recurrence.id
    assert retrieved.title == "Test Recurrence"


@pytest.mark.asyncio
async def test_update_recurrence_service(recurrence_service, db_session):
    recurrence = Recurrence(title="Test Recurrence", rrule="FREQ=DAILY;INTERVAL=1")
    db_session.add(recurrence)
    await db_session.commit()

    updated_data = RecurrenceUpdate(
        title="Updated Recurrence", rrule="FREQ=WEEKLY;BYDAY=MO"
    )
    updated = await recurrence_service.update(recurrence.id, updated_data)
    assert updated.title == "Updated Recurrence"
    assert updated.rrule == "FREQ=WEEKLY;BYDAY=MO"


@pytest.mark.asyncio
async def test_delete_recurrence_service(recurrence_service, db_session):
    new_recurrence = Recurrence(title="Test Recurrence", rrule="FREQ=DAILY;INTERVAL=1")
    db_session.add(new_recurrence)
    await db_session.commit()

    await recurrence_service.delete(new_recurrence.id)
    deleted = await RecurrenceRepository(db_session).get_by_id(new_recurrence.id)
    assert deleted is None
