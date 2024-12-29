import pytest
from app.models import Task
from app.repositories.task_repository import TaskRepository


@pytest.mark.asyncio
async def test_create_task(db_session):
    repo = TaskRepository(db_session)

    new_task = await repo.create({"title": "New Task"})
    db_session.add(new_task)
    await db_session.commit()

    assert new_task.title == "New Task"


@pytest.mark.asyncio
async def test_get_task_by_id(db_session):
    repo = TaskRepository(db_session)

    task = Task(title="Task 1")
    db_session.add(task)
    await db_session.commit()

    retrieved = await repo.get_by_id(task.id)
    assert retrieved.id == task.id
    assert retrieved.title == "Task 1"


@pytest.mark.asyncio
async def test_update_task(db_session):
    repo = TaskRepository(db_session)

    task = Task(title="Task 1")
    db_session.add(task)
    await db_session.commit()

    updated_task = await repo.update(task.id, {"title": "Updated Task"})
    assert updated_task.title == "Updated Task"


@pytest.mark.asyncio
async def test_delete_task(db_session):
    repo = TaskRepository(db_session)

    task = Task(title="Task 1")
    db_session.add(task)
    await db_session.commit()

    await repo.delete(task.id)
    deleted = await repo.get_by_id(task.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_all_tasks(db_session):
    repo = TaskRepository(db_session)

    task1 = Task(title="Task 1")
    task2 = Task(title="Task 2")

    db_session.add_all([task1, task2])
    await db_session.commit()

    tasks = await repo.get_all()
    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"
