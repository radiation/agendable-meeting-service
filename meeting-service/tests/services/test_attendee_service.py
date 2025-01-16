import pytest
from app.db.models import Attendee
from app.exceptions import NotFoundError
from app.schemas import AttendeeCreate, AttendeeUpdate


@pytest.mark.asyncio
async def test_create_attendee_service(attendee_service, db_session):
    new_attendee = AttendeeCreate(meeting_id=1, user_id=1, is_scheduler=True)
    created_attendee = await attendee_service.create(new_attendee)
    assert created_attendee.meeting_id == 1
    assert created_attendee.user_id == 1
    assert created_attendee.is_scheduler is True


@pytest.mark.asyncio
async def test_get_attendee_service(attendee_service, db_session):
    attendee = Attendee(meeting_id=1, user_id=2, is_scheduler=False)
    db_session.add(attendee)
    await db_session.commit()

    retrieved_attendee = await attendee_service.get_by_id(attendee.id)
    assert retrieved_attendee.id == attendee.id
    assert retrieved_attendee.user_id == 2
    assert retrieved_attendee.is_scheduler is False


@pytest.mark.asyncio
async def test_update_attendee_service(attendee_service, db_session):
    attendee = Attendee(meeting_id=1, user_id=3, is_scheduler=False)
    db_session.add(attendee)
    await db_session.commit()

    update_data = AttendeeUpdate(is_scheduler=True)
    updated_attendee = await attendee_service.update(attendee.id, update_data)
    assert updated_attendee.is_scheduler is True


@pytest.mark.asyncio
async def test_delete_attendee_service(attendee_service, db_session):
    attendee = Attendee(meeting_id=1, user_id=4, is_scheduler=False)
    db_session.add(attendee)
    await db_session.commit()

    # Delete the attendee
    await attendee_service.delete(attendee.id)

    # Verify the attendee no longer exists
    with pytest.raises(NotFoundError) as exc_info:
        await attendee_service.get_by_id(attendee.id)

    # Assert the correct error message
    assert exc_info.value.detail == f"Attendee with ID {attendee.id} not found"


@pytest.mark.asyncio
async def test_get_attendees_by_meeting_service(attendee_service, db_session):
    attendee1 = Attendee(meeting_id=1, user_id=5, is_scheduler=False)
    attendee2 = Attendee(meeting_id=1, user_id=6, is_scheduler=True)
    db_session.add_all([attendee1, attendee2])
    await db_session.commit()

    attendees = await attendee_service.get_by_field(field_name="meeting_id", value=1)
    assert len(attendees) == 2


@pytest.mark.asyncio
async def test_get_meetings_by_user_service(attendee_service, db_session):
    attendee1 = Attendee(meeting_id=2, user_id=7, is_scheduler=False)
    attendee2 = Attendee(meeting_id=3, user_id=7, is_scheduler=True)
    db_session.add_all([attendee1, attendee2])
    await db_session.commit()

    meetings = await attendee_service.get_by_field(field_name="user_id", value=7)
    assert len(meetings) == 2
