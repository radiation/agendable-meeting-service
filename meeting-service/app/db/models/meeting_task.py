import sqlalchemy.sql.functions as func
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship

from . import Base


class MeetingTask(Base):
    __tablename__ = "meeting_tasks"
    __table_args__ = (
        Index("ix_meeting_task_meeting_id", "meeting_id"),
        Index("ix_meeting_task_task_id", "task_id"),
    )

    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    meeting = relationship("Meeting", back_populates="tasks")
    task = relationship("Task", back_populates="meeting_tasks")
