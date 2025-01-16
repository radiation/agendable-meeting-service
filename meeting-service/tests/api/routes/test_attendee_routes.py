import pytest

attendee_data = {
    "meeting_id": 1,
    "user_id": 2,
    "is_scheduler": False,
}


@pytest.mark.asyncio
async def test_attendee_router_lifecycle(test_client):
    # Create a meeting
    response = await test_client.post(
        "/attendees/",
        json=attendee_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meeting_id"] == 1
    attendee_id = data["id"]

    # List all meetings
    response = await test_client.get("/attendees/")
    assert response.status_code == 200
    attendees = response.json()
    assert isinstance(attendees, list)

    # Get the meeting we created
    response = await test_client.get(f"/attendees/{attendee_id}")
    assert response.status_code == 200
    attendee = response.json()
    assert attendee["id"] == 1

    # Update the meeting we created
    attendee_id = response.json()["id"]
    response = await test_client.put(
        f"/attendees/{attendee_id}",
        json={
            "meeting_id": 2,
            "user_id": 2,
            "is_scheduler": False,
        },
    )
    assert response.status_code == 200
    updated_attendee = response.json()
    assert updated_attendee["meeting_id"] == 2

    # Delete the meeting we created
    response = await test_client.delete(f"/attendees/{attendee_id}")
    assert response.status_code == 204
