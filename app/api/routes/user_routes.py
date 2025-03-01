from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.decorators import log_execution_time
from app.core.dependencies import get_user_service
from app.core.logging_config import logger
from app.exceptions import NotFoundError, handle_service_exceptions
from app.schemas.user_schemas import UserCreate, UserRetrieve, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.post("/", response_model=UserRetrieve)
@handle_service_exceptions
@log_execution_time
async def create_user(
    user: UserCreate, service: UserService = Depends(get_user_service)
) -> UserRetrieve:
    logger.info(f"Creating user with data: {user.model_dump()}")
    return UserRetrieve.model_validate(await service.create(user))


@router.get("/", response_model=list[UserRetrieve])
@log_execution_time
async def get_users(
    service: UserService = Depends(get_user_service),
) -> list[UserRetrieve]:
    logger.info("Fetching all users.")
    result = await service.get_all()
    logger.info(f"Retrieved {len(result)} users.")
    return [UserRetrieve.model_validate(user) for user in result]


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
    return UserRetrieve.model_validate(result)


@router.get("/by-email/{email}", response_model=UserRetrieve)
@log_execution_time
async def get_user_by_email(
    email: str, service: UserService = Depends(get_user_service)
) -> UserRetrieve:
    logger.info(f"Fetching user with email: {email}")
    result = await service.get_by_field("email", email)
    if result is None:
        logger.warning(f"User with email {email} not found")
        raise NotFoundError(f"User with email {email} not found")
    logger.info(f"User retrieved: {result}")
    return UserRetrieve.model_validate(result[0])


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
    return UserRetrieve.model_validate(result)


@router.delete("/{user_id}", status_code=204)
@log_execution_time
async def delete_user(
    user_id: UUID, service: UserService = Depends(get_user_service)
) -> None:
    logger.info(f"Deleting user with ID: {user_id}")
    success = await service.delete(user_id)
    if not success:
        logger.warning(f"User with ID {user_id} not found")
        raise NotFoundError(f"User with ID {user_id} not found")
    logger.info(f"User with ID {user_id} deleted successfully.")
