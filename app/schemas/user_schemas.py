from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    id: UUID


class UserUpdate(UserBase):
    pass


class UserRetrieve(UserBase):
    id: UUID
    model_config = {"from_attributes": True}


# For adding users to a meeting
class AddUsersRequest(BaseModel):
    user_ids: list[UUID]
