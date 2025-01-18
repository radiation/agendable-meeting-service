from uuid import UUID

from app.core.decorators import log_execution_time
from app.core.dependencies import get_user_service
from app.core.logging_config import logger
from app.exceptions import NotFoundError, ValidationError
from app.schemas import UserCreate, UserRetrieve, UserUpdate
from app.services import UserService
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/", response_model=UserRetrieve)
@log_execution_time
async def create_user(
    user: UserCreate, service: UserService = Depends(get_user_service)
) -> UserRetrieve:
    try:
        logger.info(f"Creating user with data: {user.model_dump()}")
        result = await service.create(user)
        logger.info(f"User created successfully with ID: {result.id}")
        return result
    except ValidationError as ve:
        logger.warning(f"Validation error: {ve}")
        raise
    except Exception:
        logger.exception("Unexpected error while creating user")
        raise ValidationError("An unexpected error occurred. Please try again.")


@router.get("/", response_model=list[UserRetrieve])
@log_execution_time
async def get_users(
    service: UserService = Depends(get_user_service),
) -> list[UserRetrieve]:
    logger.info("Fetching all users.")
    result = await service.get_all()
    logger.info(f"Retrieved {len(result)} users.")
    return result


@router.get("/{user_id}", response_model=UserRetrieve)
@log_execution_time
async def get_user(
    user_id: UUID, service: UserService = Depends(get_user_service)
) -> UserRetrieve:
    logger.info(f"Fetching user with ID: {user_id}")
    result = await service.get_by_id(user_id)
    if result is None:
        logger.warning(f"User with ID {user_id} not found")
        raise NotFoundError(f"User with ID {user_id} not found")
    logger.info(f"User retrieved: {result}")
    return result


@router.put("/{user_id}", response_model=UserRetrieve)
@log_execution_time
async def update_user(
    user_id: UUID,
    user: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserRetrieve:
    logger.info(f"Updating user with ID: {user_id} with data: {user.model_dump()}")
    result = await service.update(user_id, user)
    if result is None:
        logger.warning(f"User with ID {user_id} not found")
        raise NotFoundError(f"User with ID {user_id} not found")
    logger.info(f"User updated successfully: {result}")
    return result


@router.delete("/{user_id}", status_code=204)
@log_execution_time
async def delete_user(user_id: UUID, service: UserService = Depends(get_user_service)):
    logger.info(f"Deleting user with ID: {user_id}")
    success = await service.delete(user_id)
    if not success:
        logger.warning(f"User with ID {user_id} not found")
        raise NotFoundError(f"User with ID {user_id} not found")
    logger.info(f"User with ID {user_id} deleted successfully.")
