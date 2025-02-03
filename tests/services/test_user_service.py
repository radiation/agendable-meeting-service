import pytest

from app.exceptions import NotFoundError
from app.schemas.user_schemas import UserUpdate
from tests.factories import UserCreateFactory


@pytest.mark.asyncio
async def test_create_user_service(user_service):
    user_create_factory = UserCreateFactory.build()
    created_user = await user_service.create(user_create_factory)
    assert created_user.email == user_create_factory.email
    assert created_user.first_name == user_create_factory.first_name
    assert created_user.last_name == user_create_factory.last_name


@pytest.mark.asyncio
async def test_get_user_service(user_service):
    user_create_factory = UserCreateFactory.build()
    created_user = await user_service.create(user_create_factory)

    retrieved_user = await user_service.get_by_id(created_user.id)
    assert retrieved_user.email == user_create_factory.email
    assert retrieved_user.first_name == user_create_factory.first_name
    assert retrieved_user.last_name == user_create_factory.last_name


@pytest.mark.asyncio
async def test_update_user_service(user_service):
    user_create_factory = UserCreateFactory.build()
    created_user = await user_service.create(user_create_factory)

    update_data = UserUpdate(first_name="Updated", last_name="Name")

    updated_user = await user_service.update(created_user.id, update_data)
    assert updated_user.first_name == update_data.first_name
    assert updated_user.last_name == update_data.last_name


@pytest.mark.asyncio
async def test_delete_user_service(user_service):
    user_create_factory = UserCreateFactory.build()
    created_user = await user_service.create(user_create_factory)

    await user_service.delete(created_user.id)

    with pytest.raises(NotFoundError):
        await user_service.get_by_id(created_user.id)
