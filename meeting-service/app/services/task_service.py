from datetime import datetime

from app.db.models import MeetingTask, Task
from app.db.repositories.task_repo import TaskRepository
from app.errors import NotFoundError
from app.schemas.task_schemas import TaskCreate, TaskRetrieve, TaskUpdate
from app.services.base_service import BaseService


class TaskService(BaseService[Task, TaskCreate, TaskUpdate]):
    def __init__(self, repo: TaskRepository):
        super().__init__(repo)

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
