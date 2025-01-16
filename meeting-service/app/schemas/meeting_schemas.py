from datetime import datetime
from typing import Optional

from app.schemas.recurrence_schemas import RecurrenceRetrieve
from pydantic import BaseModel, ConfigDict


class MeetingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    num_reschedules: Optional[int] = None
    reminder_sent: Optional[bool] = None
    completed: Optional[bool] = None


class MeetingCreate(MeetingBase):
    start_date: datetime
    end_date: datetime
    duration: Optional[int] = None
    recurrence_id: Optional[int] = None


class MeetingUpdate(MeetingBase):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration: Optional[int] = None
    recurrence_id: Optional[int] = None


class MeetingRetrieve(MeetingBase):
    id: int
    start_date: datetime
    end_date: datetime
    duration: int
    recurrence: Optional[RecurrenceRetrieve]


class MeetingCreateBatch(BaseModel):
    base_meeting: MeetingCreate
    dates: list[datetime]
