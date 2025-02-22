import pytest

from app.exceptions import NotFoundError
from app.schemas.meeting_schemas import MeetingUpdate
from tests.factories import MeetingCreateFactory


@pytest.mark.asyncio
async def test_create_meeting_service(meeting_service):
    meeting_create_factory = MeetingCreateFactory.build()
    created_meeting = await meeting_service.create(meeting_create_factory)
    assert created_meeting.title == meeting_create_factory.title
    assert created_meeting.duration == meeting_create_factory.duration


@pytest.mark.asyncio
async def test_get_meeting_service(meeting_service):
    meeting_create_factory = MeetingCreateFactory.build()
    created_meeting = await meeting_service.create(meeting_create_factory)

    retrieved_meeting = await meeting_service.get_by_id(created_meeting.id)
    assert retrieved_meeting.title == meeting_create_factory.title
    assert retrieved_meeting.duration == meeting_create_factory.duration


@pytest.mark.asyncio
async def test_update_meeting_service(meeting_service):
    meeting_create_factory = MeetingCreateFactory.build()
    created_meeting = await meeting_service.create(meeting_create_factory)

    update_data = MeetingUpdate(title="Updated Test Meeting", duration=120)

    updated_meeting = await meeting_service.update(created_meeting.id, update_data)
    assert updated_meeting.title == update_data.title
    assert updated_meeting.duration == update_data.duration


@pytest.mark.asyncio
async def test_delete_meeting_service(meeting_service):
    meeting_create_factory = MeetingCreateFactory.build()
    created_meeting = await meeting_service.create(meeting_create_factory)

    await meeting_service.delete(created_meeting.id)

    with pytest.raises(NotFoundError):
        await meeting_service.get_by_id(created_meeting.id)
