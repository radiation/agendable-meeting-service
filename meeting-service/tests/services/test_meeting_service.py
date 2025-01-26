from datetime import datetime

import pytest
from app.db.models import Meeting
from app.exceptions import NotFoundError
from app.schemas import MeetingCreate, MeetingUpdate


@pytest.mark.asyncio
async def test_create_meeting_service(meeting_service, db_session):
    new_meeting = MeetingCreate(
        title="Service Test Meeting",
        start_date=datetime.now(),
        duration=60,
    )
    created_meeting = await meeting_service.create(new_meeting)
    assert created_meeting.title == "Service Test Meeting"
    assert created_meeting.duration == 60


@pytest.mark.asyncio
async def test_get_meeting_service(meeting_service, db_session):
    meeting = Meeting(
        title="Test Meeting",
        start_date=datetime.now(),
        duration=60,
    )
    db_session.add(meeting)
    await db_session.commit()

    retrieved_meeting = await meeting_service.get_by_id(meeting.id)
    assert retrieved_meeting.title == "Test Meeting"
    assert retrieved_meeting.duration == 60


@pytest.mark.asyncio
async def test_update_meeting_service(meeting_service, db_session):
    meeting = Meeting(
        title="Test Meeting",
        start_date=datetime.now(),
        duration=60,
    )
    db_session.add(meeting)
    await db_session.commit()

    update_data = MeetingUpdate(title="Updated Test Meeting", duration=120)
    updated_meeting = await meeting_service.update(meeting.id, update_data)
    assert updated_meeting.title == "Updated Test Meeting"
    assert updated_meeting.duration == 120


@pytest.mark.asyncio
async def test_delete_meeting_service(meeting_service, db_session):
    meeting = Meeting(
        title="Test Meeting",
        start_date=datetime.now(),
        duration=60,
    )
    db_session.add(meeting)
    await db_session.commit()

    await meeting_service.delete(meeting.id)

    # Verify that the meeting is deleted
    with pytest.raises(NotFoundError):
        await meeting_service.get_by_id(meeting.id)
