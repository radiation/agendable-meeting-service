from app.models import MeetingTask
from app.repositories.meeting_task_repository import MeetingTaskRepository
from app.schemas.meeting_task_schemas import MeetingTaskCreate, MeetingTaskUpdate
from app.schemas.task_schemas import TaskRetrieve
from app.services.base import BaseService


class MeetingTaskService(
    BaseService[MeetingTask, MeetingTaskCreate, MeetingTaskUpdate]
):
    def __init__(self, repository: MeetingTaskRepository):
        super().__init__(repository)

    async def get_tasks_by_meeting(self, meeting_id: int) -> list[TaskRetrieve]:
        # Fetch meeting tasks associated with the given meeting_id
        tasks = await self.repository.get_tasks_by_meeting(meeting_id)
        return tasks
