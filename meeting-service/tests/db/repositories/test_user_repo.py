import uuid

import pytest
from app.db.models import User
from app.db.repositories import UserRepository


@pytest.mark.asyncio
async def test_create_user(db_session):
    repo = UserRepository(db_session)

    new_user = await repo.create(
        {
            "id": uuid.uuid4(),
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        }
    )
    db_session.add(new_user)
    await db_session.commit()

    assert new_user.email == "test@example.com"
    assert new_user.first_name == "Test"
    assert new_user.last_name == "User"


@pytest.mark.asyncio
async def test_get_user_by_id(db_session):
    repo = UserRepository(db_session)

    user = User(
        id=uuid.uuid4(), email="test@example.com", first_name="Test", last_name="User"
    )
    db_session.add(user)
    await db_session.commit()

    retrieved = await repo.get_by_id(user.id)
    assert retrieved.id == user.id
    assert retrieved.email == "test@example.com"
    assert retrieved.first_name == "Test"
    assert retrieved.last_name == "User"


@pytest.mark.asyncio
async def test_update_user(db_session):
    repo = UserRepository(db_session)

    user = User(
        id=uuid.uuid4(), email="test@example.com", first_name="Test", last_name="User"
    )
    db_session.add(user)
    await db_session.commit()

    updated_user = await repo.update(
        user.id, {"first_name": "Updated", "last_name": "Name"}
    )
    assert updated_user.first_name == "Updated"
    assert updated_user.last_name == "Name"


@pytest.mark.asyncio
async def test_delete_user(db_session):
    repo = UserRepository(db_session)

    user = User(
        id=uuid.uuid4(), email="test@example.com", first_name="Test", last_name="User"
    )
    db_session.add(user)
    await db_session.commit()

    await repo.delete(user.id)
    deleted = await repo.get_by_id(user.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_all_users(db_session):
    repo = UserRepository(db_session)

    user1 = User(
        id=uuid.uuid4(), email="test1@example.com", first_name="First", last_name="User"
    )
    user2 = User(
        id=uuid.uuid4(),
        email="test2@example.com",
        first_name="Second",
        last_name="User",
    )

    db_session.add_all([user1, user2])
    await db_session.commit()

    users = await repo.get_all()
    assert len(users) == 2
    assert users[0].email == "test1@example.com"
    assert users[1].email == "test2@example.com"
