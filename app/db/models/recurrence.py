from datetime import datetime, timedelta

from dateutil.rrule import rrulestr
from sqlalchemy import Column, DateTime, Index, Integer, String
from sqlalchemy.orm import relationship
import sqlalchemy.sql.functions as func

from app.core.logging_config import logger

from . import Base


class Recurrence(Base):
    """
    Store the RFC 5545 recurrence rule string
    rrules aren't TZ aware so these will always be UTC

    Examples:
    FREQ=WEEKLY;BYDAY=TU;BYHOUR=17;BYMINUTE=30
    FREQ=MONTHLY;BYMONTHDAY=15;BYHOUR=9;BYMINUTE=0
    FREQ=YEARLY;BYMONTH=6;BYMONTHDAY=24;BYHOUR=12;BYMINUTE=0
    """

    __tablename__ = "recurrences"
    __table_args__ = (
        Index("ix_recurrence_rrule", "rrule"),
        Index("ix_recurrence_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True)
    title = Column(String(100), default="")
    rrule = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meetings = relationship("Meeting", back_populates="recurrence")

    def get_next_date(self, start_date: datetime, duration: int = 60) -> datetime:
        """Generate the next occurrence date based on the recurrence rule."""
        try:
            rule = rrulestr(self.rrule, dtstart=start_date)
            next_date = rule.after(start_date + timedelta(minutes=duration), inc=False)
            logger.debug(f"Start date: {start_date}, Next date: {next_date}")
            return next_date
        except Exception as exc:
            raise ValueError(
                f"Invalid recurrence rule: {self.rrule}. Error: {str(exc)}"
            ) from exc

    def __repr__(self):
        return f"<Recurrence(title={self.title}, rrule={self.rrule})>"
