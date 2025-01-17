import pytest
from app.db.models import User
from app.exceptions import NotFoundError
from app.schemas import UserCreate, UserUpdate


@pytest.mark.asyncio
async def test_create_user(user_service):
    new_user = UserCreate(email="test@example.com", first_name="Test", last_name="User")
    created_user = await user_service.create(new_user)

    assert created_user.email == "test@example.com"
    assert created_user.first_name == "Test"
    assert created_user.last_name == "User"


@pytest.mark.asyncio
async def test_get_user_by_id(user_service):
    user_data = UserCreate(
        email="test@example.com", first_name="Test", last_name="User"
    )
    created_user = await user_service.create(user_data)

    retrieved_user = await user_service.get_by_id(created_user.id)
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.first_name == "Test"
    assert retrieved_user.last_name == "User"


@pytest.mark.asyncio
async def test_update_user(user_service):
    user_data = UserCreate(
        email="test@example.com", first_name="Test", last_name="User"
    )
    created_user = await user_service.create(user_data)

    update_data = UserUpdate(first_name="Updated", last_name="Name")
    updated_user = await user_service.update(created_user.id, update_data)

    assert updated_user.first_name == "Updated"
    assert updated_user.last_name == "Name"


@pytest.mark.asyncio
async def test_delete_user(user_service, db_session):
    user_data = UserCreate(
        email="test@example.com", first_name="Test", last_name="User"
    )
    created_user = await user_service.create(user_data)

    await user_service.delete(created_user.id)

    # Verify that the user is deleted
    with pytest.raises(NotFoundError):
        await user_service.get_by_id(created_user.id)


@pytest.mark.asyncio
async def test_get_users_by_email(user_service, db_session):
    user1 = User(email="test1@example.com", first_name="First", last_name="User")
    user2 = User(email="test2@example.com", first_name="Second", last_name="User")

    db_session.add_all([user1, user2])
    await db_session.commit()

    users = await user_service.get_by_field(
        field_name="email", value="test1@example.com"
    )
    assert len(users) == 1
    assert users[0].email == "test1@example.com"
