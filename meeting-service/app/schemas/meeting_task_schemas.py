from pydantic import BaseModel, ConfigDict


class MeetingTaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    meeting_id: int
    task_id: int


class MeetingTaskCreate(MeetingTaskBase):
    pass


class MeetingTaskUpdate(MeetingTaskBase):
    pass


class MeetingTaskRetrieve(MeetingTaskBase):
    id: int
