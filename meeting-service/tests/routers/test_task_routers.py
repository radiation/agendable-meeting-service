import pytest

task_data = {
    "title": "New Task",
    "assignee_id": 1,
    "due_date": "2024-01-01T09:00:00Z",
    "description": "Monthly review task",
    "completed": False,
    "completed_date": "2024-01-01T09:00:00Z",
}

"""
We test the entire lifecycle of a task in a single test because we can't
guarantee the order of execution of tests.
"""


@pytest.mark.asyncio
async def test_task_router_lifecycle(test_client):
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
