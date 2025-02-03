from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = False
    completed_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    title: str
    assignee_id: int
    completed: Optional[bool] = False


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    assignee_id: Optional[int] = None
    completed: Optional[bool] = None


class TaskRetrieve(BaseModel):
    id: int
    title: str
    assignee_id: Optional[int]
    completed: bool
    completed_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    model_config = {"from_attributes": True}
