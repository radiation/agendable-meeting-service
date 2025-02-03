import pytest

from app.exceptions import NotFoundError
from app.schemas.task_schemas import TaskUpdate
from tests.factories import TaskCreateFactory


@pytest.mark.asyncio
async def test_create_task_service(task_service):
    task_create_factory = TaskCreateFactory.build()
    created_task = await task_service.create(task_create_factory)
    assert created_task.title == task_create_factory.title


@pytest.mark.asyncio
async def test_get_task_service(task_service):
    task_create_factory = TaskCreateFactory.build()
    created_task = await task_service.create(task_create_factory)

    retrieved_task = await task_service.get_by_id(created_task.id)
    assert retrieved_task.title == task_create_factory.title


@pytest.mark.asyncio
async def test_update_task_service(task_service):
    task_create_factory = TaskCreateFactory.build()
    created_task = await task_service.create(task_create_factory)

    update_data = TaskUpdate(title="Updated Test Task")
    updated_task = await task_service.update(created_task.id, update_data)
    assert updated_task.title == updated_task.title


@pytest.mark.asyncio
async def test_delete_task_service(task_service):
    task_create_factory = TaskCreateFactory.build()
    created_task = await task_service.create(task_create_factory)

    await task_service.delete(created_task.id)

    with pytest.raises(NotFoundError):
        await task_service.get_by_id(created_task.id)
