import pytest

meeting_task_data = {
    "meeting_id": 1,
    "task_id": 1,
}

"""
We test the entire lifecycle of a task in a single test because we can't
guarantee the order of execution of tests.
"""


@pytest.mark.asyncio
async def test_task_router_lifecycle(test_client):
    # Create a meeting_task
    response = await test_client.post(
        "/meeting_tasks/",
        json=meeting_task_data,
    )
    assert response.status_code == 200
    meeting_task_id = response.json()["id"]

    # List all meeting_tasks
    response = await test_client.get("/meeting_tasks/")
    assert response.status_code == 200
    meeting_tasks = response.json()
    assert isinstance(meeting_tasks, list)

    # Get the meeting_task we created
    response = await test_client.get(f"/meeting_tasks/{meeting_task_id}")
    assert response.status_code == 200
    meeting_task = response.json()
    assert meeting_task["id"] == meeting_task_id

    # Update the meeting_task we created
    response = await test_client.put(
        f"/meeting_tasks/{meeting_task_id}",
        json={
            "id": meeting_task_id,
            "meeting_id": 2,
            "task_id": 1,
        },
    )
    assert response.status_code == 200
    updated_meeting_task = response.json()
    assert updated_meeting_task["meeting_id"] == 2

    # Delete the meeting_task we created
    response = await test_client.delete(f"/meeting_tasks/{meeting_task_id}")
    assert response.status_code == 204

    # Verify deletion
    response = await test_client.get(f"/meeting_tasks/{meeting_task_id}")
    assert response.status_code == 404
