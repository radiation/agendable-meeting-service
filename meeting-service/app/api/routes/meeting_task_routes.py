from typing import List

from app.core.decorators import log_execution_time
from app.core.dependencies import get_meeting_task_service
from app.core.logging_config import logger
from app.exceptions import NotFoundError, ValidationError
from app.schemas.meeting_task_schemas import (
    MeetingTaskCreate,
    MeetingTaskRetrieve,
    MeetingTaskUpdate,
)
from app.services.meeting_task_service import MeetingTaskService
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/", response_model=MeetingTaskRetrieve)
@log_execution_time
async def create_meeting_task(
    task: MeetingTaskCreate,
    service: MeetingTaskService = Depends(get_meeting_task_service),
) -> MeetingTaskRetrieve:
    logger.info(f"Creating meeting task with data: {task.model_dump()}")
    try:
        result = await service.create(task)
        logger.info(f"Meeting task created successfully with ID: {result.id}")
        return result
    except ValidationError as ve:
        logger.warning(f"Validation error: {ve}")
        raise
    except Exception:
        logger.exception("Unexpected error while creating meeting task")
        raise ValidationError(detail="An unexpected error occurred. Please try again.")


@router.get("/", response_model=List[MeetingTaskRetrieve])
@log_execution_time
async def get_meeting_tasks(
    skip: int = 0,
    limit: int = 10,
    service: MeetingTaskService = Depends(get_meeting_task_service),
) -> List[MeetingTaskRetrieve]:
    logger.info(f"Fetching all meeting tasks with skip={skip} and limit={limit}")
    result = await service.get_all(skip=skip, limit=limit)
    logger.info(f"Retrieved {len(result)} meeting tasks.")
    return result


@router.get("/{meeting_task_id}", response_model=MeetingTaskRetrieve)
@log_execution_time
async def get_meeting_task(
    meeting_task_id: int,
    service: MeetingTaskService = Depends(get_meeting_task_service),
) -> MeetingTaskRetrieve:
    logger.info(f"Fetching meeting task with ID: {meeting_task_id}")
    result = await service.get_by_id(meeting_task_id)
    if result is None:
        logger.warning(f"Meeting task with ID {meeting_task_id} not found")
        raise NotFoundError(detail="Meeting task not found")
    logger.info(f"Meeting task retrieved: {result}")
    return result


@router.put("/{meeting_task_id}", response_model=MeetingTaskRetrieve)
@log_execution_time
async def update_meeting_task(
    meeting_task_id: int,
    meeting_task: MeetingTaskUpdate,
    service: MeetingTaskService = Depends(get_meeting_task_service),
) -> MeetingTaskRetrieve:
    logger.info(
        f"Updating meeting task with ID: {meeting_task_id} \
            with data: {meeting_task.model_dump()}"
    )
    result = await service.update(meeting_task_id, meeting_task)
    if result is None:
        logger.warning(f"Meeting task with ID {meeting_task_id} not found")
        raise NotFoundError(detail="Meeting task not found")
    logger.info(f"Meeting task updated successfully: {result}")
    return result


@router.delete("/{meeting_task_id}", status_code=204)
@log_execution_time
async def delete_meeting_task(
    meeting_task_id: int,
    service: MeetingTaskService = Depends(get_meeting_task_service),
):
    logger.info(f"Deleting meeting task with ID: {meeting_task_id}")
    success = await service.delete(meeting_task_id)
    if not success:
        logger.warning(f"Meeting task with ID {meeting_task_id} not found")
        raise NotFoundError(detail="Meeting task not found")
    logger.info(f"Meeting task with ID {meeting_task_id} deleted successfully.")


@router.get("/by_meeting/{meeting_id}", response_model=List[MeetingTaskRetrieve])
@log_execution_time
async def read_tasks_by_meeting(
    meeting_id: int, service: MeetingTaskService = Depends(get_meeting_task_service)
) -> List[MeetingTaskRetrieve]:
    logger.info(f"Fetching all meeting tasks for meeting with ID: {meeting_id}")
    result = await service.get_by_id(meeting_id)
    logger.info(f"Retrieved {len(result)} meeting tasks for meeting ID: {meeting_id}")
    return result
