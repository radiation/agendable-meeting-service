import json

import pytest

from tests.factories import MeetingFactory


@pytest.mark.asyncio
async def test_meeting_router_lifecycle(test_client):
    # Generate meeting data using the factory
    meeting_data = MeetingFactory.as_dict()

    # Create a meeting
    response = await test_client.post(
        "/meetings/",
        json=meeting_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == meeting_data["title"]
    meeting_id = data["id"]

    # List all meetings
    response = await test_client.get("/meetings/")
    assert response.status_code == 200
    meetings = response.json()
    assert isinstance(meetings, list)

    # Get the meeting we created
    response = await test_client.get(f"/meetings/{meeting_id}")
    assert response.status_code == 200
    meeting = response.json()
    assert meeting["id"] == meeting_id
    assert meeting["title"] == meeting_data["title"]

    # Update the meeting we created
    updated_meeting_data = MeetingFactory.as_dict(title="Updated Team Meeting")
    response = await test_client.put(
        f"/meetings/{meeting_id}",
        json=updated_meeting_data,
    )
    assert response.status_code == 200
    updated_meeting = response.json()
    assert updated_meeting["title"] == "Updated Team Meeting"

    # Delete the meeting we created
    response = await test_client.delete(f"/meetings/{meeting_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_meeting_with_recurrence_id(test_client):
    # Create a meeting recurrence
    recurrence_data = {
        "title": "Annual Meeting",
        "rrule": "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=24;BYHOUR=12;BYMINUTE=0",
    }
    response = await test_client.post(
        "/recurrences/",
        json=recurrence_data,
    )
    recurrence = response.json()
    assert recurrence["title"] == "Annual Meeting"
    recurrence_id = recurrence["id"]

    # Generate meeting data with recurrence ID
    meeting_data = MeetingFactory.as_dict(recurrence_id=recurrence_id)

    # Create a meeting with the recurrence ID
    response = await test_client.post(
        "/meetings/",
        json=meeting_data,
    )
    assert response.status_code == 200, f"Failed to create meeting: {response.json()}"

    meeting = response.json()
    assert meeting["title"] == meeting_data["title"]
    assert meeting["recurrence"]["rrule"] == recurrence_data["rrule"]
    assert meeting["recurrence"]["title"] == recurrence_data["title"]


@pytest.mark.asyncio
async def test_complete_meeting(test_client, mock_redis_client):
    # Generate meeting data
    meeting_data = MeetingFactory.as_dict()

    # Create a meeting
    response = await test_client.post(
        "/meetings/",
        json=meeting_data,
    )
    meeting = response.json()
    meeting_id = meeting["id"]

    # Complete the meeting with validation error
    response = await test_client.post(f"/meetings/{meeting_id}/complete/")
    assert response.status_code == 400

    recurrence_data = {
        "title": "Annual Meeting",
        "rrule": "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=24;BYHOUR=12;BYMINUTE=0",
    }
    response = await test_client.post(
        "/recurrences/",
        json=recurrence_data,
    )
    recurrence = response.json()
    assert recurrence["title"] == "Annual Meeting"
    recurrence_id = recurrence["id"]

    meeting_data["recurrence_id"] = recurrence_id
    response = await test_client.post(
        "/meetings/",
        json=meeting_data,
    )
    meeting = response.json()
    meeting_id = meeting["id"]

    # Complete the meeting with no errors
    response = await test_client.post(f"/meetings/{meeting_id}/complete/")
    assert response.status_code == 200

    mock_redis_client.publish.assert_awaited_with(
        "meeting-events",
        json.dumps(
            {
                "event_type": "complete",
                "model": "Meeting",
                "payload": {
                    "meeting_id": meeting_id,
                    "next_meeting_id": int(meeting_id) + 1,
                },
            }
        ),
    )

    # Validate completion
    response = await test_client.get(f"/meetings/{meeting_id}")
    meeting = response.json()
    assert meeting["completed"] is True


@pytest.mark.asyncio
async def test_get_next_meeting(test_client):
    # Generate meeting data
    meeting_data = MeetingFactory.as_dict()

    # Create a meeting
    response = await test_client.post(
        "/meetings/",
        json=meeting_data,
    )
    meeting = response.json()
    meeting_id = meeting["id"]

    # Add a recurrence to the meeting
    recurrence_data = {
        "title": "Annual Meeting",
        "rrule": "FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=24;BYHOUR=12;BYMINUTE=0",
    }
    response = await test_client.post(
        "/recurrences/",
        json=recurrence_data,
    )
    recurrence = response.json()
    assert recurrence["title"] == "Annual Meeting"
    recurrence_id = recurrence["id"]
    response = await test_client.post(
        f"/meetings/{meeting_id}/add_recurrence/{recurrence_id}",
    )
    meeting = response.json()

    # Get the next meeting
    response = await test_client.get(f"/meetings/{meeting_id}/next/")
    assert response.status_code == 200
    next_meeting = response.json()
    assert next_meeting["recurrence"] == meeting["recurrence"]
