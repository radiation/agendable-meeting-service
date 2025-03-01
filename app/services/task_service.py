from uuid import UUID

from app.core.logging_config import logger
from app.db.models.task import Task
from app.db.repositories.task_repo import TaskRepository
from app.exceptions import NotFoundError
from app.schemas.task_schemas import TaskCreate, TaskRetrieve, TaskUpdate
from app.services import BaseService


class TaskService(BaseService[Task, TaskCreate, TaskUpdate]):
    def __init__(
        self,
        repo: TaskRepository,
        redis_client=None,
    ):
        super().__init__(repo, redis_client=redis_client)

    async def mark_task_complete(self, task_id: int) -> TaskRetrieve:
        logger.info(f"Marking task with ID {task_id} as complete")
        task = await self.repo.mark_task_complete(task_id)
        if not task:
            logger.warning(f"Task with ID {task_id} not found")
            raise NotFoundError(detail=f"Task with ID {task_id} not found")
        return TaskRetrieve.model_validate(task)

    async def reassign_tasks_to_meeting(
        self, source_meeting_id: int, target_meeting_id: int
    ) -> None:
        logger.info(
            f"Reassigning tasks from M:{source_meeting_id} to M:{target_meeting_id}"
        )

        # Fetch incomplete tasks for the source meeting
        tasks = await self.repo.get_incomplete_tasks_for_meeting(source_meeting_id)
        if not tasks:
            logger.info(f"No incomplete tasks for meeting ID {source_meeting_id}")
            return

        # Reassign tasks to the target meeting
        task_ids = [task.id for task in tasks]
        await self.repo.reassign_tasks_to_meeting(task_ids, target_meeting_id)
        logger.info(
            f"Reassigned {len(task_ids)} tasks to meeting ID {target_meeting_id}"
        )

    async def get_tasks_by_meeting(self, meeting_id: int) -> list[TaskRetrieve]:
        logger.info(f"Fetching tasks for meeting ID {meeting_id}")
        tasks = await self.repo.get_tasks_by_meeting(meeting_id)
        logger.info(f"Retrieved {len(tasks)} tasks for meeting ID {meeting_id}")
        return [TaskRetrieve.model_validate(task) for task in tasks]

    async def get_tasks_by_user(self, assignee_id: UUID) -> list[TaskRetrieve]:
        logger.info(f"Fetching tasks for user ID {assignee_id}")
        tasks = await self.repo.get_tasks_by_user(assignee_id)
        logger.info(f"Retrieved {len(tasks)} tasks for user ID {assignee_id}")
        return [TaskRetrieve.model_validate(task) for task in tasks]
