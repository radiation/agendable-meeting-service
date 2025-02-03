from datetime import datetime
from typing import List, Optional

from app.schemas.meeting_recurrence_schemas import MeetingRecurrenceRetrieve
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
    duration: int
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
    recurrence: Optional[MeetingRecurrenceRetrieve]


class MeetingCreateBatch(BaseModel):
    base_meeting: MeetingCreate
    dates: List[datetime]
