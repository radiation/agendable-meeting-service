import pytest
from app.models import MeetingRecurrence
from app.repositories.meeting_recurrence_repository import MeetingRecurrenceRepository


@pytest.mark.asyncio
async def test_create_meeting_recurrence(db_session):
    repo = MeetingRecurrenceRepository(db_session)

    new_recurrence = {
        "title": "Test Recurrence",
        "rrule": "FREQ=DAILY;INTERVAL=1",
    }
    meeting_recurrence = await repo.create(new_recurrence)
    assert meeting_recurrence.title == "Test Recurrence"
    assert meeting_recurrence.rrule == "FREQ=DAILY;INTERVAL=1"


@pytest.mark.asyncio
async def test_get_meeting_recurrence(db_session):
    repo = MeetingRecurrenceRepository(db_session)

    # Create a test recurrence
    meeting_recurrence = MeetingRecurrence(
        title="Test Recurrence", rrule="FREQ=DAILY;INTERVAL=1"
    )
    db_session.add(meeting_recurrence)
    await db_session.commit()

    # Fetch the recurrence
    retrieved = await repo.get_by_id(meeting_recurrence.id)
    assert retrieved.id == meeting_recurrence.id
    assert retrieved.title == "Test Recurrence"


@pytest.mark.asyncio
async def test_delete_meeting_recurrence(db_session):
    repo = MeetingRecurrenceRepository(db_session)

    # Create a test recurrence
    meeting_recurrence = MeetingRecurrence(
        title="Test Recurrence", rrule="FREQ=DAILY;INTERVAL=1"
    )
    db_session.add(meeting_recurrence)
    await db_session.commit()

    # Delete the recurrence
    await repo.delete(meeting_recurrence.id)
    deleted = await repo.get_by_id(meeting_recurrence.id)
    assert deleted is None
