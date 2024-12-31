from app.core.dependencies import get_task_service
from app.schemas import task_schemas
from app.services.task_service import TaskService
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/", response_model=task_schemas.TaskRetrieve)
async def create_task(
    task: task_schemas.TaskCreate, service: TaskService = Depends(get_task_service)
) -> task_schemas.TaskRetrieve:
    return await service.create(task)


@router.get("/", response_model=list[task_schemas.TaskRetrieve])
async def get_tasks(
    service: TaskService = Depends(get_task_service),
) -> list[task_schemas.TaskRetrieve]:
    return await service.get_by_field(field_name="assignee_id", value=None)


@router.get("/{task_id}", response_model=task_schemas.TaskRetrieve)
async def get_task(
    task_id: int, service: TaskService = Depends(get_task_service)
) -> task_schemas.TaskRetrieve:
    return await service.get_by_id(task_id)


@router.put("/{task_id}", response_model=task_schemas.TaskRetrieve)
async def update_task(
    task_id: int,
    task: task_schemas.TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> task_schemas.TaskRetrieve:
    return await service.update(task_id, task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    await service.delete(task_id)


@router.get("/user/{user_id}", response_model=list[task_schemas.TaskRetrieve])
async def get_tasks_by_user(
    user_id: int, service: TaskService = Depends(get_task_service)
) -> list[task_schemas.TaskRetrieve]:
    return await service.get_tasks_by_user(user_id)


@router.post("/{task_id}/complete", response_model=task_schemas.TaskRetrieve)
async def complete_task(
    task_id: int, service: TaskService = Depends(get_task_service)
) -> task_schemas.TaskRetrieve:
    return await service.mark_task_complete(task_id)
