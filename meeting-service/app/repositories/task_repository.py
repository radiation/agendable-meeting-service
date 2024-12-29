from datetime import datetime

from app.models import Task
from app.repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def mark_task_complete(self, task_id: int) -> Task:
        task = await self.get_by_id(task_id)
        if not task:
            return None  # Task not found
        if task.completed:
            return task  # Task already completed
        task.completed = True
        task.completed_date = datetime.utcnow()
        await self.db.commit()
        return task
