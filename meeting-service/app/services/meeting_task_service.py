from app.db.models import MeetingTask
from app.db.repositories.meeting_task_repo import MeetingTaskRepository
from app.schemas.meeting_task_schemas import MeetingTaskCreate, MeetingTaskUpdate
from app.schemas.task_schemas import TaskRetrieve
from app.services.base_service import BaseService
from loguru import logger


class MeetingTaskService(
    BaseService[MeetingTask, MeetingTaskCreate, MeetingTaskUpdate]
):
    def __init__(self, repo: MeetingTaskRepository):
        super().__init__(repo, model_name="MeetingTask")

    async def get_tasks_by_meeting(self, meeting_id: int) -> list[TaskRetrieve]:
        logger.info(f"Fetching tasks for meeting with ID: {meeting_id}")
        tasks = await self.repo.get_tasks_by_meeting(meeting_id)
        logger.info(f"Retrieved {len(tasks)} tasks for meeting with ID: {meeting_id}")
        return tasks
