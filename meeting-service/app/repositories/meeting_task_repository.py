from app.models import MeetingTask, Task
from app.repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class MeetingTaskRepository(BaseRepository[MeetingTask]):
    def __init__(self, db: AsyncSession):
        super().__init__(MeetingTask, db)

    async def get_tasks_by_meeting(self, meeting_id: int) -> list[Task]:
        stmt = (
            select(Task)
            .join(MeetingTask, MeetingTask.task_id == Task.id)
            .where(MeetingTask.meeting_id == meeting_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
