from datetime import datetime

from app.core.logging_config import logger
from app.db.models import Task
from app.db.repositories import TaskRepository
from app.exceptions import NotFoundError
from app.schemas import TaskCreate, TaskRetrieve, TaskUpdate
from app.services import BaseService
from sqlalchemy.exc import NoResultFound


class TaskService(BaseService[Task, TaskCreate, TaskUpdate]):
    def __init__(self, repo: TaskRepository):
        super().__init__(repo, model_name="Task")

    async def mark_task_complete(self, task_id: int) -> TaskRetrieve:
        logger.info(f"Marking task with ID {task_id} as complete")
        task = await self.repo.mark_task_complete(task_id)
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
    ) -> TaskRetrieve:
        try:
            meeting = await self.meeting_repo.get_by_id(meeting_id)
            if not meeting:
                raise ValueError(f"Meeting with ID {meeting_id} not found.")
        except NoResultFound:
            raise ValueError(f"Meeting with ID {meeting_id} not found.")

        task_data = {
            "title": task_title,
            "assignee_id": assignee_id,
            "due_date": due_date,
        }
        new_task = await self.task_repo.create(task_data)

        # TODO: Move this to repo layer
        meeting.tasks.append(new_task)

        await self.db.commit()
        await self.db.refresh(new_task)

        return new_task
