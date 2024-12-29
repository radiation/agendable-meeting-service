from datetime import datetime, timedelta

import pytest
from app.models import Meeting, MeetingAttendee, MeetingRecurrence
from app.repositories.meeting_repository import MeetingRepository


@pytest.mark.asyncio
async def test_create_meeting(db_session):
    repo = MeetingRepository(db_session)

    new_meeting = {
        "title": "Test Meeting",
        "start_date": datetime.now(),
        "end_date": datetime.now() + timedelta(hours=1),
        "duration": 60,
    }
    meeting = await repo.create(new_meeting)
    assert meeting.title == "Test Meeting"
    assert meeting.duration == 60


@pytest.mark.asyncio
async def test_get_meeting_by_id(db_session):
    repo = MeetingRepository(db_session)

    meeting = Meeting(
        title="Test Meeting",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(hours=1),
        duration=60,
    )
    db_session.add(meeting)
    await db_session.commit()

    retrieved = await repo.get_by_id(meeting.id)
    assert retrieved.title == "Test Meeting"
    assert retrieved.duration == 60


@pytest.mark.asyncio
async def test_get_meeting_by_user(db_session):
    repo = MeetingRepository(db_session)

    # Create and commit a sample meeting
    meeting = Meeting(
        title="Test Meeting",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(hours=1),
        duration=60,
    )
    db_session.add(meeting)
    await db_session.commit()

    # Use the repository's get_by_field method
    retrieved_meetings: list[Meeting] = await repo.get_by_field("title", "Test Meeting")

    # Assertions
    assert len(retrieved_meetings) == 1
    assert retrieved_meetings[0] is not None
    assert retrieved_meetings[0].title == "Test Meeting"
    assert retrieved_meetings[0].duration == 60
    assert retrieved_meetings[0].id == meeting.id


@pytest.mark.asyncio
async def test_update_meeting(db_session):
    repo = MeetingRepository(db_session)

    meeting = Meeting(
        title="Test Meeting",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(hours=1),
        duration=60,
    )
    db_session.add(meeting)
    await db_session.commit()

    updated_data = {"title": "Updated Meeting", "duration": 120}
    updated_meeting = await repo.update(meeting.id, updated_data)
    assert updated_meeting.title == "Updated Meeting"
    assert updated_meeting.duration == 120


@pytest.mark.asyncio
async def test_delete_meeting(db_session):
    repo = MeetingRepository(db_session)

    meeting = Meeting(
        title="Test Meeting",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(hours=1),
        duration=60,
    )
    db_session.add(meeting)
    await db_session.commit()

    await repo.delete(meeting.id)
    deleted = await repo.get_by_id(meeting.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_relationships(db_session):
    # Add a recurrence
    recurrence = MeetingRecurrence(
        title="Weekly Recurrence", rrule="FREQ=WEEKLY;INTERVAL=1"
    )
    db_session.add(recurrence)
    await db_session.commit()

    # Create a meeting
    meeting = Meeting(
        title="Test Meeting",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(hours=1),
        duration=60,
        recurrence_id=recurrence.id,
    )
    db_session.add(meeting)
    await db_session.commit()

    # Add attendees
    attendees = [
        MeetingAttendee(meeting_id=meeting.id, user_id=1),
        MeetingAttendee(meeting_id=meeting.id, user_id=2),
    ]
    db_session.add_all(attendees)
    await db_session.commit()

    # Query the meeting with relationships
    repo = MeetingRepository(db_session)
    result = await repo.get_by_id(meeting.id)

    # Assertions
    assert result is not None
    assert result.recurrence.title == "Weekly Recurrence"
    assert len(result.attendees) == 2
    assert {attendee.user_id for attendee in result.attendees} == {1, 2}
