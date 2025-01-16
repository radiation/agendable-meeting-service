import sqlalchemy.sql.functions as func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship

from . import Base


class Attendee(Base):
    __tablename__ = "attendees"
    __table_args__ = (
        Index("ix_attendee_meeting_id", "meeting_id"),
        Index("ix_attendee_user_id", "user_id"),
        Index("ix_attendee_meeting_user", "meeting_id", "user_id"),
    )

    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    user_id = Column(Integer)
    is_scheduler = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    meeting = relationship("Meeting", back_populates="attendees")
