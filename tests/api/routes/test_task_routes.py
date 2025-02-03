import pytest

from tests.factories import TaskFactory


@pytest.mark.asyncio
async def test_task_router_lifecycle(test_client):
    task_data = TaskFactory.as_dict()

    # Create a task
    response = await test_client.post(
        "/tasks/",
        json=task_data,
    )
    assert response.status_code == 200
    task_id = response.json()["id"]

    # List all tasks
    response = await test_client.get("/tasks/")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)

    # Get the task we created
    response = await test_client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == task_id

    # Update the task we created
    response = await test_client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "assignee_id": 1,
            "due_date": "2024-01-01T09:00:00Z",
            "description": "Updated review task",
            "completed": False,
            "completed_date": "2024-01-01T09:00:00Z",
        },
    )
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["title"] == "Updated Task"

    # Delete the task we created
    response = await test_client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify deletion
    response = await test_client.get(f"/tasks/{task_id}")
    assert response.status_code == 404
