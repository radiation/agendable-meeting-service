from app.db.models import MeetingTask
from app.db.repositories.meeting_task_repo import MeetingTaskRepository
from app.schemas.meeting_task_schemas import MeetingTaskCreate, MeetingTaskUpdate
from app.schemas.task_schemas import TaskRetrieve
from app.services.base_service import BaseService


class MeetingTaskService(
    BaseService[MeetingTask, MeetingTaskCreate, MeetingTaskUpdate]
):
    def __init__(self, repo: MeetingTaskRepository):
        super().__init__(repo)

    async def get_tasks_by_meeting(self, meeting_id: int) -> list[TaskRetrieve]:
        # Fetch meeting tasks associated with the given meeting_id
        tasks = await self.repo.get_tasks_by_meeting(meeting_id)
        return tasks
