from datetime import datetime

from app.errors import NotFoundError
from app.models import MeetingTask, Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task_schemas import TaskCreate, TaskRetrieve, TaskUpdate
from app.services.base import BaseService


class TaskService(BaseService[Task, TaskCreate, TaskUpdate]):
    def __init__(self, repository: TaskRepository):
        super().__init__(repository)

    async def mark_task_complete(self, task_id: int) -> TaskRetrieve:
        task = await self.task_repo.mark_task_complete(task_id)
        if not task:
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
