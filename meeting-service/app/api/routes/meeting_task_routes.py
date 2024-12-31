from typing import List

from app.core.dependencies import get_meeting_task_service
from app.schemas.meeting_task_schemas import (
    MeetingTaskCreate,
    MeetingTaskRetrieve,
    MeetingTaskUpdate,
)
from app.services.meeting_task_service import MeetingTaskService
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/", response_model=MeetingTaskRetrieve)
async def create_meeting_task(
    task: MeetingTaskCreate,
    service: MeetingTaskService = Depends(get_meeting_task_service),
) -> MeetingTaskRetrieve:
    return await service.create(task)


@router.get("/", response_model=List[MeetingTaskRetrieve])
async def read_meeting_tasks(
    skip: int = 0,
    limit: int = 10,
    service: MeetingTaskService = Depends(get_meeting_task_service),
) -> List[MeetingTaskRetrieve]:
    return await service.get_all(skip=skip, limit=limit)


@router.get("/{meeting_task_id}", response_model=MeetingTaskRetrieve)
async def get_meeting_task(
    meeting_task_id: int,
    service: MeetingTaskService = Depends(get_meeting_task_service),
) -> MeetingTaskRetrieve:
    return await service.get_by_id(meeting_task_id)


@router.put("/{meeting_task_id}", response_model=MeetingTaskRetrieve)
async def update_meeting_task(
    meeting_task_id: int,
    meeting_task: MeetingTaskUpdate,
    service: MeetingTaskService = Depends(get_meeting_task_service),
) -> MeetingTaskRetrieve:
    return await service.update(meeting_task_id, meeting_task)


@router.delete("/{meeting_task_id}", status_code=204)
async def delete_meeting_task(
    meeting_task_id: int,
    service: MeetingTaskService = Depends(get_meeting_task_service),
):
    await service.delete(meeting_task_id)


@router.get("/by_meeting/{meeting_id}", response_model=List[MeetingTaskRetrieve])
async def read_tasks_by_meeting(
    meeting_id: int, service: MeetingTaskService = Depends(get_meeting_task_service)
) -> List[MeetingTaskRetrieve]:
    return await service.get_by_id(meeting_id)
