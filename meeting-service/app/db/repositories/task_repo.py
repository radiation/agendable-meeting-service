from datetime import datetime

from app.core.logging_config import logger
from app.db.models import Task
from app.db.repositories.base_repo import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def mark_task_complete(self, task_id: int) -> Task:
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
