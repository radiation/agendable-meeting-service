import datetime

from dateutil.rrule import rrulestr
from pydantic import BaseModel, field_validator


class RecurrenceBase(BaseModel):
    model_config = {"from_attributes": True}
    rrule: str
    title: str = ""


class RecurrenceCreate(RecurrenceBase):
    @field_validator("rrule")
    def validate_rrule(cls, value):
        try:
            # Attempt to parse the rule to ensure its validity
            rrulestr(value, dtstart=datetime.datetime.now())
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid recurrence rule: {str(e)}")
        return value


class RecurrenceUpdate(BaseModel):
    model_config = {"from_attributes": True}
    rrule: str | None = None
    title: str | None = None


class RecurrenceRetrieve(RecurrenceBase):
    id: int
