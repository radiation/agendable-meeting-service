from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)

    meetings = relationship(
        "Meeting", secondary="meeting_users", back_populates="users"
    )

    def __repr__(self):
        return f"<User {self.email}>"
