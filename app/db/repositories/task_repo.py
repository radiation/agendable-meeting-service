from datetime import datetime

from app.core.logging_config import logger
from app.db.models import Task, meeting_tasks
from app.db.repositories import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def mark_task_complete(self, task_id: int) -> Task:
        """
        Mark a task as complete.
        :param task_id: ID of the task to mark as complete.
        :return: Task object.
        """
        logger.debug(f"Marking task with ID {task_id} as complete")
        task = await self.get_by_id(task_id)
        if not task:
            logger.warning(f"Task with ID {task_id} not found")
            return None
        if task.completed:
            logger.info(f"Task with ID {task_id} is already completed")
            return task
        task.completed = True
        task.completed_date = datetime.now()
        await self.db.commit()
        logger.debug(f"Task with ID {task_id} marked as complete")
        return task

    async def get_incomplete_tasks_for_meeting(self, meeting_id: int) -> list[Task]:
        """
        Fetch all incomplete tasks for a meeting.
        :param meeting_id: ID of the meeting.
        :return: List of Task objects.
        """
        logger.info(f"Fetching incomplete tasks for meeting ID {meeting_id}")
        stmt = (
            select(self.model)
            .join(meeting_tasks, meeting_tasks.c.task_id == self.model.id)
            .where(
                meeting_tasks.c.meeting_id == meeting_id,
                self.model.completed is False,
            )
        )
        result = await self.db.execute(stmt)
        tasks = result.scalars().all()
        logger.debug(f"Found {len(tasks)} incomplete tasks for meeting ID {meeting_id}")
        return tasks

    async def reassign_tasks_to_meeting(self, task_ids: list[int], new_meeting_id: int):
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
