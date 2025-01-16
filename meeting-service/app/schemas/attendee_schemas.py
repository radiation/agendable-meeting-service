from typing import Optional

from pydantic import BaseModel, ConfigDict


class AttendeeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    meeting_id: int
    user_id: int
    is_scheduler: Optional[bool] = False


class AttendeeCreate(AttendeeBase):
    pass


class AttendeeUpdate(BaseModel):
    model_config = {"from_attributes": True}
    meeting_id: Optional[int] = None
    user_id: Optional[int] = None
    is_scheduler: Optional[bool] = None


class AttendeeRetrieve(AttendeeBase):
    id: int
