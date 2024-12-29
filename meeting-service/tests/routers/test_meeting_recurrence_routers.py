import pytest


@pytest.mark.asyncio
async def test_get_meeting_recurrences(test_client):
    response = await test_client.get("/meeting_recurrences/")
    assert response.status_code == 200
    meeting_recurrences = response.json()
    assert isinstance(meeting_recurrences, list)
