from datetime import datetime
from typing import Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.logging_config import logger
from app.db.models.relationships import meeting_tasks, task_assignees
from app.db.models.task import Task
from app.db.repositories import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def mark_task_complete(self, task_id: int) -> Optional[Task]:
        logger.debug(f"Marking task with ID {task_id} as complete")
        task = await self.get_by_id(task_id)
        if not task:
            logger.warning(f"Task with ID {task_id} not found")
            return None
        if task.completed:
            logger.info(f"Task with ID {task_id} is already completed")
            return task
        await self.db.execute(
            update(Task)
            .where(Task.id == task.id)
            .values(completed=True, completed_date=datetime.now())
        )
        await self.db.commit()
        logger.debug(f"Task with ID {task_id} marked as complete")
        return task

    async def get_incomplete_tasks_for_meeting(self, meeting_id: int) -> list[Task]:
        logger.info(f"Fetching incomplete tasks for meeting ID {meeting_id}")
        stmt = (
            select(self.model)
            .join(meeting_tasks, meeting_tasks.c.task_id == self.model.id)
            .where(
                meeting_tasks.c.meeting_id == meeting_id,
                self.model.completed.is_(False),
            )
        )
        result = await self.db.execute(stmt)
        tasks = list(result.scalars().all())
        logger.debug(f"Found {len(tasks)} incomplete tasks for meeting ID {meeting_id}")
        return tasks

    async def reassign_tasks_to_meeting(
        self, task_ids: list[int], new_meeting_id: int
    ) -> None:
        logger.info(f"Reassigning tasks {task_ids} to meeting ID {new_meeting_id}")
        stmt = (
            meeting_tasks.update()
            .where(meeting_tasks.c.task_id.in_(task_ids))
            .values(meeting_id=new_meeting_id)
        )
        try:
            await self.db.execute(stmt)
            await self.db.commit()
            logger.info(
                f"Successfully reassigned {len(task_ids)} tasks to M:{new_meeting_id}"
            )
        except Exception as e:
            logger.error(f"Error reassigning tasks: {e}")
            await self.db.rollback()
            raise

    async def get_tasks_by_meeting(self, meeting_id: int) -> list[Task]:
        logger.info(f"Fetching tasks for meeting ID {meeting_id}")
        stmt = (
            select(self.model)
            .join(meeting_tasks, meeting_tasks.c.task_id == self.model.id)
            .where(meeting_tasks.c.meeting_id == meeting_id)
        )
        result = await self.db.execute(stmt)
        tasks = list(result.scalars().all())
        logger.info(f"Retrieved {len(tasks)} tasks for meeting ID {meeting_id}")
        return tasks

    async def get_tasks_by_user(self, user_id: int) -> list[Task]:
        logger.info(f"Fetching tasks assigned to user with ID {user_id}")
        stmt = (
            select(self.model)
            .join(task_assignees, task_assignees.c.task_id == self.model.id)
            .where(task_assignees.c.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        tasks = list(result.scalars().all())
        logger.info(f"Retrieved {len(tasks)} tasks for user ID {user_id}")
        return tasks
