from typing import Generic, TypeVar

from app.errors import NotFoundError
from app.repositories.base import BaseRepository
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    def _get_model_name(self) -> str:
        return self.repository.model.__name__

    async def create(self, create_data: CreateSchemaType) -> ModelType:
        return await self.repository.create(create_data.model_dump())

    async def get_by_id(self, id: int) -> ModelType:
        entity = await self.repository.get_by_id(id)
        if not entity:
            raise NotFoundError(
                detail=f"{self._get_model_name()} with ID {id} not found"
            )
        return entity

    async def get_by_field(self, field_name: str, value: any) -> list[ModelType]:
        return await self.repository.get_by_field(field_name, value)

    async def get_all(self, skip: int = 0, limit: int = 10) -> list[ModelType]:
        return await self.repository.get_all(skip, limit)

    async def update(self, id: int, update_data: UpdateSchemaType) -> ModelType:
        entity = await self.repository.get_by_id(id)
        if not entity:
            raise NotFoundError(
                detail=f"{self._get_model_name()} with ID {id} not found"
            )
        return await self.repository.update(
            id, update_data.model_dump(exclude_unset=True)
        )

    async def delete(self, id: int) -> bool:
        entity = await self.repository.get_by_id(id)
        if not entity:
            raise NotFoundError(
                detail=f"{self._get_model_name()} with ID {id} not found"
            )
        return await self.repository.delete(id)
