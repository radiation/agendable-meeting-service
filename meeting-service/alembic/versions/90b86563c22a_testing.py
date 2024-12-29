"""Testing

Revision ID: 90b86563c22a
Revises: 40b72a62f358
Create Date: 2024-12-29 11:49:27.681342

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "90b86563c22a"
down_revision: Union[str, None] = "40b72a62f358"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        "ix_meeting_attendee_meeting_id",
        "meeting_attendees",
        ["meeting_id"],
        unique=False,
    )
    op.create_index(
        "ix_meeting_attendee_meeting_user",
        "meeting_attendees",
        ["meeting_id", "user_id"],
        unique=False,
    )
    op.create_index(
        "ix_meeting_attendee_user_id", "meeting_attendees", ["user_id"], unique=False
    )
    op.create_index(
        "ix_meeting_recurrence_created_at",
        "meeting_recurrences",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_meeting_recurrence_rrule", "meeting_recurrences", ["rrule"], unique=False
    )
    op.create_index(
        "ix_meeting_task_meeting_id", "meeting_tasks", ["meeting_id"], unique=False
    )
    op.create_index(
        "ix_meeting_task_task_id", "meeting_tasks", ["task_id"], unique=False
    )
    op.create_index("ix_meeting_completed", "meetings", ["completed"], unique=False)
    op.create_index(
        "ix_meeting_recurrence_id", "meetings", ["recurrence_id"], unique=False
    )
    op.create_index("ix_meeting_start_date", "meetings", ["start_date"], unique=False)
    op.create_index("ix_task_assignee_id", "tasks", ["assignee_id"], unique=False)
    op.create_index("ix_task_completed", "tasks", ["completed"], unique=False)
    op.create_index("ix_task_due_date", "tasks", ["due_date"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_task_due_date", table_name="tasks")
    op.drop_index("ix_task_completed", table_name="tasks")
    op.drop_index("ix_task_assignee_id", table_name="tasks")
    op.drop_index("ix_meeting_start_date", table_name="meetings")
    op.drop_index("ix_meeting_recurrence_id", table_name="meetings")
    op.drop_index("ix_meeting_completed", table_name="meetings")
    op.drop_index("ix_meeting_task_task_id", table_name="meeting_tasks")
    op.drop_index("ix_meeting_task_meeting_id", table_name="meeting_tasks")
    op.drop_index("ix_meeting_recurrence_rrule", table_name="meeting_recurrences")
    op.drop_index("ix_meeting_recurrence_created_at", table_name="meeting_recurrences")
    op.drop_index("ix_meeting_attendee_user_id", table_name="meeting_attendees")
    op.drop_index("ix_meeting_attendee_meeting_user", table_name="meeting_attendees")
    op.drop_index("ix_meeting_attendee_meeting_id", table_name="meeting_attendees")
    # ### end Alembic commands ###
