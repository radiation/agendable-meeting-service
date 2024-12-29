import datetime

from dateutil.rrule import rrulestr
from pydantic import BaseModel, field_validator


class MeetingRecurrenceBase(BaseModel):
    model_config = {"from_attributes": True}
    rrule: str
    title: str = ""


class MeetingRecurrenceCreate(MeetingRecurrenceBase):
    @field_validator("rrule")
    def validate_rrule(cls, value):
        try:
            # Attempt to parse the rule to ensure its validity
            rrulestr(value, dtstart=datetime.datetime.now())
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid recurrence rule: {str(e)}")
        return value


class MeetingRecurrenceUpdate(BaseModel):
    model_config = {"from_attributes": True}
    rrule: str | None = None
    title: str | None = None


class MeetingRecurrenceRetrieve(MeetingRecurrenceBase):
    id: int
