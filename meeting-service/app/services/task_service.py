from datetime import datetime

from app.db.models import MeetingTask, Task
from app.db.repositories.task_repo import TaskRepository
from app.exceptions import NotFoundError
from app.schemas.task_schemas import TaskCreate, TaskRetrieve, TaskUpdate
from app.services.base_service import BaseService
from loguru import logger


class TaskService(BaseService[Task, TaskCreate, TaskUpdate]):
    def __init__(self, repo: TaskRepository):
        super().__init__(repo, model_name="Task")

    async def mark_task_complete(self, task_id: int) -> TaskRetrieve:
        logger.info(f"Marking task with ID {task_id} as complete")
        task = await self.task_repo.mark_task_complete(task_id)
        if not task:
            logger.warning(f"Task with ID {task_id} not found")
            raise NotFoundError(detail=f"Task with ID {task_id} not found")
        return TaskRetrieve.model_validate(task)

    async def create_new_meeting_task(
        self,
        meeting_id: int,
        task_title: str,
        assignee_id: int,
        due_date: datetime = None,
    ) -> MeetingTask:
        # TODO: Logic to create a meeting task
        pass
