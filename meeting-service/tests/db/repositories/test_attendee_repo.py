import pytest
from app.db.models import Attendee
from app.db.repositories import AttendeeRepository


@pytest.mark.asyncio
async def test_create_attendee(db_session):
    repo = AttendeeRepository(db_session)

    new_attendee = {
        "meeting_id": 1,
        "user_id": 1,
        "is_scheduler": True,
    }
    attendee = await repo.create(new_attendee)
    assert attendee.meeting_id == 1
    assert attendee.user_id == 1
    assert attendee.is_scheduler is True


@pytest.mark.asyncio
async def test_get_attendee_by_id(db_session):
    repo = AttendeeRepository(db_session)

    attendee = Attendee(meeting_id=1, user_id=2, is_scheduler=False)
    db_session.add(attendee)
    await db_session.commit()

    retrieved = await repo.get_by_id(attendee.id)
    assert retrieved.id == attendee.id
    assert retrieved.user_id == 2
    assert retrieved.is_scheduler is False


@pytest.mark.asyncio
async def test_update_attendee(db_session):
    repo = AttendeeRepository(db_session)

    attendee = Attendee(meeting_id=1, user_id=3, is_scheduler=False)
    db_session.add(attendee)
    await db_session.commit()

    updated_data = {"is_scheduler": True}
    updated_attendee = await repo.update(attendee.id, updated_data)
    assert updated_attendee.is_scheduler is True


@pytest.mark.asyncio
async def test_delete_attendee(db_session):
    repo = AttendeeRepository(db_session)

    attendee = Attendee(meeting_id=1, user_id=4, is_scheduler=False)
    db_session.add(attendee)
    await db_session.commit()

    await repo.delete(attendee.id)
    deleted_attendee = await repo.get_by_id(attendee.id)
    assert deleted_attendee is None
