import sqlalchemy.sql.functions as func
from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String
from sqlalchemy.orm import relationship

from . import Base, meeting_tasks


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_task_assignee_id", "assignee_id"),
        Index("ix_task_due_date", "due_date"),
        Index("ix_task_completed", "completed"),
    )

    id = Column(Integer, primary_key=True)
    assignee_id = Column(Integer)
    title = Column(String(100), default="")
    description = Column(String(1000), default="")
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed = Column(Boolean, default=False)
    completed_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    meetings = relationship("Meeting", secondary=meeting_tasks, back_populates="tasks")
