import pytest

meeting_attendee_data = {
    "meeting_id": 1,
    "user_id": 2,
    "is_scheduler": False,
}


@pytest.mark.asyncio
async def test_meeting_attendee_router_lifecycle(test_client):
    # Create a meeting
    response = await test_client.post(
        "/meeting_attendees/",
        json=meeting_attendee_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meeting_id"] == 1
    meeting_attendee_id = data["id"]

    # List all meetings
    response = await test_client.get("/meeting_attendees/")
    assert response.status_code == 200
    meeting_attendees = response.json()
    assert isinstance(meeting_attendees, list)

    # Get the meeting we created
    response = await test_client.get(f"/meeting_attendees/{meeting_attendee_id}")
    assert response.status_code == 200
    meeting_attendee = response.json()
    assert meeting_attendee["id"] == 1

    # Update the meeting we created
    meeting_attendee_id = response.json()["id"]
    response = await test_client.put(
        f"/meeting_attendees/{meeting_attendee_id}",
        json={
            "meeting_id": 2,
            "user_id": 2,
            "is_scheduler": False,
        },
    )
    assert response.status_code == 200
    updated_meeting_attendee = response.json()
    assert updated_meeting_attendee["meeting_id"] == 2

    # Delete the meeting we created
    response = await test_client.delete(f"/meeting_attendees/{meeting_attendee_id}")
    assert response.status_code == 204
