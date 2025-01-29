import pytest
from app.db.models import Meeting, Recurrence
from app.db.repositories import MeetingRepository
from tests.factories import MeetingFactory


@pytest.mark.asyncio
async def test_create_meeting(db_session):
    repo = MeetingRepository(db_session)
    meeting_data = MeetingFactory.build()
    created_meeting = await repo.create(meeting_data)

    assert created_meeting.title == meeting_data.title
    assert created_meeting.start_date == meeting_data.start_date


@pytest.mark.asyncio
async def test_get_meeting_by_id(db_session):
    repo = MeetingRepository(db_session)

    meeting_data = MeetingFactory.build()
    created_meeting = await repo.create(meeting_data)

    retrieved = await repo.get_by_id(created_meeting.id)
    assert retrieved.title == meeting_data.title
    assert retrieved.duration == meeting_data.duration


# TODO: Have this test actually test getting a meeting by user
@pytest.mark.asyncio
async def test_get_meeting_by_user(db_session):
    repo = MeetingRepository(db_session)

    meeting_data = MeetingFactory.build()
    created_meeting = await repo.create(meeting_data)
    assert created_meeting is not None

    # Use the repo's get_by_field method
    retrieved_meetings: list[Meeting] = await repo.get_by_field(
        "title", meeting_data.title
    )

    # Assertions
    assert len(retrieved_meetings) == 1
    assert retrieved_meetings[0] is not None
    assert retrieved_meetings[0].title == meeting_data.title
    assert retrieved_meetings[0].duration == meeting_data.duration
    assert retrieved_meetings[0].id == created_meeting.id


@pytest.mark.asyncio
async def test_update_meeting(db_session):
    repo = MeetingRepository(db_session)

    meeting_data = MeetingFactory.build()
    created_meeting = await repo.create(meeting_data)
    assert created_meeting is not None

    updated_data = Meeting(title="Updated Meeting", duration=120)
    updated_meeting = await repo.update(updated_data)
    assert updated_meeting.title == updated_data.title
    assert updated_meeting.duration == updated_data.duration


@pytest.mark.asyncio
async def test_delete_meeting(db_session):
    repo = MeetingRepository(db_session)

    meeting_data = MeetingFactory.build()
    created_meeting = await repo.create(meeting_data)

    await repo.delete(created_meeting.id)
    deleted = await repo.get_by_id(created_meeting.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_relationships(db_session):
    repo = MeetingRepository(db_session)

    recurrence = Recurrence(title="Weekly Recurrence", rrule="FREQ=WEEKLY;INTERVAL=1")
    db_session.add(recurrence)
    await db_session.commit()

    meeting_data = MeetingFactory.build(recurrence_id=recurrence.id)
    created_meeting = await repo.create(meeting_data)

    repo = MeetingRepository(db_session)
    result = await repo.get_by_id(created_meeting.id)

    assert result is not None
    assert result.recurrence.title == "Weekly Recurrence"
