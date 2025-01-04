from app.core.decorators import log_execution_time
from app.core.dependencies import get_task_service
from app.exceptions import NotFoundError, ValidationError
from app.schemas import task_schemas
from app.services.task_service import TaskService
from fastapi import APIRouter, Depends
from loguru import logger

router = APIRouter()


@router.post("/", response_model=task_schemas.TaskRetrieve)
@log_execution_time
async def create_task(
    task: task_schemas.TaskCreate, service: TaskService = Depends(get_task_service)
) -> task_schemas.TaskRetrieve:
    try:
        logger.info(f"Creating task with data: {task.model_dump()}")
        result = await service.create(task)
        logger.info(f"Task created successfully with ID: {result.id}")
        return result
    except ValidationError as ve:
        logger.warning(f"Validation error: {ve}")
        raise
    except Exception:
        logger.exception("Unexpected error while creating task")
        raise ValidationError("An unexpected error occurred. Please try again.")


@router.get("/", response_model=list[task_schemas.TaskRetrieve])
@log_execution_time
async def get_tasks(
    service: TaskService = Depends(get_task_service),
) -> list[task_schemas.TaskRetrieve]:
    logger.info("Fetching all tasks assigned to no specific assignee.")
    result = await service.get_by_field(field_name="assignee_id", value=None)
    logger.info(f"Retrieved {len(result)} tasks.")
    return result


@router.get("/{task_id}", response_model=task_schemas.TaskRetrieve)
@log_execution_time
async def get_task(
    task_id: int, service: TaskService = Depends(get_task_service)
) -> task_schemas.TaskRetrieve:
    logger.info(f"Fetching task with ID: {task_id}")
    result = await service.get_by_id(task_id)
    if result is None:
        logger.warning(f"Task with ID {task_id} not found")
        raise NotFoundError(f"Task with ID {task_id} not found")
    logger.info(f"Task retrieved: {result}")
    return result


@router.put("/{task_id}", response_model=task_schemas.TaskRetrieve)
@log_execution_time
async def update_task(
    task_id: int,
    task: task_schemas.TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> task_schemas.TaskRetrieve:
    logger.info(f"Updating task with ID: {task_id} with data: {task.model_dump()}")
    result = await service.update(task_id, task)
    if result is None:
        logger.warning(f"Task with ID {task_id} not found")
        raise NotFoundError(f"Task with ID {task_id} not found")
    logger.info(f"Task updated successfully: {result}")
    return result


@router.delete("/{task_id}", status_code=204)
@log_execution_time
async def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    logger.info(f"Deleting task with ID: {task_id}")
    success = await service.delete(task_id)
    if not success:
        logger.warning(f"Task with ID {task_id} not found")
        raise NotFoundError(f"Task with ID {task_id} not found")
    logger.info(f"Task with ID {task_id} deleted successfully.")


@router.get("/user/{user_id}", response_model=list[task_schemas.TaskRetrieve])
@log_execution_time
async def get_tasks_by_user(
    user_id: int, service: TaskService = Depends(get_task_service)
) -> list[task_schemas.TaskRetrieve]:
    logger.info(f"Fetching tasks assigned to user with ID: {user_id}")
    result = await service.get_tasks_by_user(user_id)
    logger.info(f"Retrieved {len(result)} tasks for user ID: {user_id}")
    return result


@router.post("/{task_id}/complete", response_model=task_schemas.TaskRetrieve)
@log_execution_time
async def complete_task(
    task_id: int, service: TaskService = Depends(get_task_service)
) -> task_schemas.TaskRetrieve:
    logger.info(f"Marking task with ID {task_id} as complete.")
    result = await service.mark_task_complete(task_id)
    if result is None:
        logger.warning(f"Task with ID {task_id} not found")
        raise NotFoundError(f"Task with ID {task_id} not found")
    logger.info(f"Task with ID {task_id} marked as complete.")
    return result
