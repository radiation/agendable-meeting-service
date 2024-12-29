import pytest
from app.models import MeetingTask, Task
from app.schemas.meeting_task_schemas import MeetingTaskCreate, MeetingTaskUpdate


@pytest.mark.asyncio
async def test_create_meeting_task_service(meeting_task_service):
    new_task_data = MeetingTaskCreate(meeting_id=1, task_id=1)
    created_task = await meeting_task_service.create(new_task_data)

    assert created_task.meeting_id == 1
    assert created_task.task_id == 1


@pytest.mark.asyncio
async def test_get_meeting_task_service(meeting_task_service, db_session):
    meeting_task = MeetingTask(meeting_id=1, task_id=2)
    db_session.add(meeting_task)
    await db_session.commit()

    retrieved_task = await meeting_task_service.get_by_id(meeting_task.id)
    assert retrieved_task.id == meeting_task.id
    assert retrieved_task.meeting_id == 1


@pytest.mark.asyncio
async def test_update_meeting_task_service(meeting_task_service, db_session):
    meeting_task = MeetingTask(meeting_id=1, task_id=3)
    db_session.add(meeting_task)
    await db_session.commit()

    update_data = MeetingTaskUpdate(meeting_id=2, task_id=3)
    updated_task = await meeting_task_service.update(meeting_task.id, update_data)
    assert updated_task.meeting_id == 2


@pytest.mark.asyncio
async def test_delete_meeting_task_service(meeting_task_service, db_session):
    meeting_task = MeetingTask(meeting_id=1, task_id=4)
    db_session.add(meeting_task)
    await db_session.commit()

    await meeting_task_service.delete(meeting_task.id)

    with pytest.raises(Exception):
        await meeting_task_service.get_by_id(meeting_task.id)


@pytest.mark.asyncio
async def test_get_tasks_by_meeting_service(meeting_task_service, db_session):
    task1 = Task(id=1, title="Task 1", assignee_id=10, completed=False)
    task2 = Task(id=2, title="Task 2", assignee_id=20, completed=False)
    meeting_task1 = MeetingTask(meeting_id=1, task_id=1)
    meeting_task2 = MeetingTask(meeting_id=1, task_id=2)

    db_session.add_all([task1, task2, meeting_task1, meeting_task2])
    await db_session.commit()

    # Call the service
    tasks = await meeting_task_service.get_tasks_by_meeting(meeting_id=1)

    # Validate response
    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"
