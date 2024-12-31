import pytest
from app.db.models import MeetingTask, Task
from app.db.repositories.meeting_task_repo import MeetingTaskRepository


@pytest.mark.asyncio
async def test_create_meeting_task(db_session):
    repo = MeetingTaskRepository(db_session)

    new_task = await repo.create({"meeting_id": 1, "task_id": 1})
    db_session.add(new_task)
    await db_session.commit()

    assert new_task.meeting_id == 1
    assert new_task.task_id == 1


@pytest.mark.asyncio
async def test_get_meeting_task_by_id(db_session):
    repo = MeetingTaskRepository(db_session)

    meeting_task = MeetingTask(meeting_id=1, task_id=2)
    db_session.add(meeting_task)
    await db_session.commit()

    retrieved = await repo.get_by_id(meeting_task.id)
    assert retrieved.id == meeting_task.id
    assert retrieved.meeting_id == 1


@pytest.mark.asyncio
async def test_get_tasks_by_meeting(db_session):
    repo = MeetingTaskRepository(db_session)

    task1 = Task(id=1, title="Task 1")
    task2 = Task(id=2, title="Task 2")
    meeting_task1 = MeetingTask(meeting_id=1, task_id=1)
    meeting_task2 = MeetingTask(meeting_id=1, task_id=2)

    db_session.add_all([task1, task2, meeting_task1, meeting_task2])
    await db_session.commit()

    tasks = await repo.get_tasks_by_meeting(meeting_id=1)
    assert len(tasks) == 2


@pytest.mark.asyncio
async def test_delete_meeting_task(db_session):
    repo = MeetingTaskRepository(db_session)

    meeting_task = MeetingTask(meeting_id=1, task_id=3)
    db_session.add(meeting_task)
    await db_session.commit()

    await repo.delete(meeting_task.id)
    deleted = await repo.get_by_id(meeting_task.id)
    assert deleted is None
