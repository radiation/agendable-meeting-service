import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from . import Base


class User(Base):
    __tablename__ = "users"
    id = id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)

    meetings = relationship(
        "Meeting", secondary="meeting_users", back_populates="users"
    )

    def __repr__(self):
        return f"<User {self.email}>"
