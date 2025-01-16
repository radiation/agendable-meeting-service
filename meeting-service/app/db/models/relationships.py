from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table
from sqlalchemy.sql import func

from . import Base

meeting_tasks = Table(
    "meeting_tasks",
    Base.metadata,
    Column(
        "meeting_id",
        Integer,
        ForeignKey("meetings.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
