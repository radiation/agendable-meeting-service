from datetime import datetime, timedelta

import pytest
from app.db.models.recurrence import Recurrence


@pytest.mark.asyncio
async def test_read_main(test_client):
    response = await test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Meeting Service API"}


@pytest.mark.asyncio
async def test_get_next_date(test_client):
    recurrence = Recurrence(rrule="FREQ=WEEKLY;BYDAY=MO;BYHOUR=10;BYMINUTE=0")
    start_date = datetime(2025, 1, 27, 10, 0)
    next_date = recurrence.get_next_date(start_date, duration=60)
    assert next_date > start_date + timedelta(minutes=60)
