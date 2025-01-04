from typing import Generic, TypeVar

from app.core.logging_config import logger
from app.db.repositories.base_repo import BaseRepository
from app.exceptions import NotFoundError
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, repo: BaseRepository[ModelType], model_name: str = None):
        self.repo = repo
        self.model_name = model_name or self._get_model_name()

    def _get_model_name(self) -> str:
        return self.repo.model.__name__

    async def create(self, create_data: CreateSchemaType) -> ModelType:
        logger.info(f"Creating {self.model_name} with data: {create_data.model_dump()}")
        result = await self.repo.create(create_data.model_dump())
        logger.info(f"{self.model_name} created successfully with ID: {result.id}")
        return result

    async def get_by_id(self, id: int) -> ModelType:
        logger.info(f"Fetching {self.model_name} with ID: {id}")
        entity = await self.repo.get_by_id(id)
        if not entity:
            logger.warning(f"{self.model_name} with ID {id} not found")
            raise NotFoundError(detail=f"{self.model_name} with ID {id} not found")
        logger.info(f"{self.model_name} retrieved: {entity}")
        return entity

    async def get_by_field(self, field_name: str, value: any) -> list[ModelType]:
        logger.info(f"Fetching {self.model_name} by {field_name}={value}")
        result = await self.repo.get_by_field(field_name, value)
        logger.info(
            f"Retrieved {len(result)} {self.model_name}(s) \
                matching {field_name}={value}"
        )
        return result

    async def get_all(self, skip: int = 0, limit: int = 10) -> list[ModelType]:
        logger.info(f"Fetching all {self.model_name}s with skip={skip}, limit={limit}")
        result = await self.repo.get_all(skip, limit)
        logger.info(f"Retrieved {len(result)} {self.model_name}(s)")
        return result

    async def update(self, id: int, update_data: UpdateSchemaType) -> ModelType:
        logger.info(
            f"Updating {self.model_name} with ID: {id} \
                and data: {update_data.model_dump()}"
        )
        entity = await self.repo.get_by_id(id)
        if not entity:
            logger.warning(f"{self.model_name} with ID {id} not found")
            raise NotFoundError(detail=f"{self.model_name} with ID {id} not found")
        updated_entity = await self.repo.update(
            id, update_data.model_dump(exclude_unset=True)
        )
        logger.info(f"{self.model_name} with ID {id} updated successfully")
        return updated_entity

    async def delete(self, id: int) -> bool:
        logger.info(f"Deleting {self.model_name} with ID: {id}")
        entity = await self.repo.get_by_id(id)
        if not entity:
            logger.warning(f"{self.model_name} with ID {id} not found")
            raise NotFoundError(detail=f"{self.model_name} with ID {id} not found")
        success = await self.repo.delete(id)
        if success:
            logger.info(f"{self.model_name} with ID {id} deleted successfully")
        else:
            logger.error(f"Failed to delete {self.model_name} with ID {id}")
        return success
