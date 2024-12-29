import pytest
from app.models import MeetingRecurrence
from app.repositories.meeting_recurrence_repository import MeetingRecurrenceRepository
from app.schemas.meeting_recurrence_schemas import (
    MeetingRecurrenceCreate,
    MeetingRecurrenceUpdate,
)


@pytest.mark.asyncio
async def test_create_recurrence_service(meeting_recurrence_service, db_session):
    new_recurrence = MeetingRecurrenceCreate(
        title="Service Test Recurrence", rrule="FREQ=DAILY;INTERVAL=1"
    )
    created = await meeting_recurrence_service.create(new_recurrence)
    assert created.title == "Service Test Recurrence"
    assert created.rrule == "FREQ=DAILY;INTERVAL=1"


@pytest.mark.asyncio
async def test_get_recurrence_service(meeting_recurrence_service, db_session):
    meeting_recurrence = MeetingRecurrence(
        title="Test Recurrence", rrule="FREQ=DAILY;INTERVAL=1"
    )
    db_session.add(meeting_recurrence)
    await db_session.commit()

    retrieved = await meeting_recurrence_service.get_by_id(meeting_recurrence.id)
    assert retrieved.id == meeting_recurrence.id
    assert retrieved.title == "Test Recurrence"


@pytest.mark.asyncio
async def test_update_recurrence_service(meeting_recurrence_service, db_session):
    meeting_recurrence = MeetingRecurrence(
        title="Test Recurrence", rrule="FREQ=DAILY;INTERVAL=1"
    )
    db_session.add(meeting_recurrence)
    await db_session.commit()

    updated_data = MeetingRecurrenceUpdate(
        title="Updated Recurrence", rrule="FREQ=WEEKLY;BYDAY=MO"
    )
    updated = await meeting_recurrence_service.update(
        meeting_recurrence.id, updated_data
    )
    assert updated.title == "Updated Recurrence"
    assert updated.rrule == "FREQ=WEEKLY;BYDAY=MO"


@pytest.mark.asyncio
async def test_delete_recurrence_service(meeting_recurrence_service, db_session):
    new_recurrence = MeetingRecurrence(
        title="Test Recurrence", rrule="FREQ=DAILY;INTERVAL=1"
    )
    db_session.add(new_recurrence)
    await db_session.commit()

    await meeting_recurrence_service.delete(new_recurrence.id)
    deleted = await MeetingRecurrenceRepository(db_session).get_by_id(new_recurrence.id)
    assert deleted is None
