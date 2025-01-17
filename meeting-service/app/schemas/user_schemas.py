from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    email: str
    first_name: str
    last_name: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserRetrieve(UserBase):
    id: int
    email: str
    first_name: str
    last_name: str

    model_config = {"from_attributes": True}
