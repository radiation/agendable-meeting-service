from typing import Any, Generic, Type, TypeVar, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.logging_config import logger

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, db_obj: ModelType) -> ModelType:
        logger.debug(f"Creating {self.model.__name__} with data: {db_obj}")
        self.db.add(db_obj)
        try:
            await self.db.commit()
            await self.db.refresh(db_obj)
            stmt = select(self.model).filter(self.model.id == db_obj.id)
            result = await self.db.execute(stmt)
            db_obj = result.scalars().first()
            logger.debug(
                f"{self.model.__name__} created successfully with ID: {db_obj.id}"
            )
            return db_obj
        except Exception as e:
            logger.exception(f"Error creating {self.model.__name__}: {e}")
            raise

    async def get_by_id(self, object_id: Union[int, UUID]) -> ModelType:
        logger.debug(f"Fetching {self.model.__name__} with ID: {object_id}")

        if isinstance(object_id, UUID):
            logger.debug("ID is already a UUID, skipping conversion")
        elif isinstance(self.model.id.type.python_type, type):
            logger.debug(f"Converting ID to {self.model.id.type.python_type}")
            object_id = self.model.id.type.python_type(object_id)

        stmt = select(self.model).filter(self.model.id == object_id)

        try:
            result = await self.db.execute(stmt)
            entity = result.unique().scalar()
            if not entity:
                logger.warning(f"{self.model.__name__} with ID {object_id} not found")
            else:
                logger.debug(f"Retrieved {self.model.__name__}: {entity}")
            return entity
        except Exception as e:
            logger.exception(
                f"Error fetching {self.model.__name__} with ID {object_id}: {e}"
            )
            raise

    async def get_all(self, skip: int = 0, limit: int = 10) -> list[ModelType]:
        logger.debug(
            f"Fetching all {self.model.__name__} with skip={skip}, limit={limit}"
        )
        stmt = select(self.model).offset(skip).limit(limit)
        try:
            result = await self.db.execute(stmt)
            entities = result.unique().scalars().all()
            logger.debug(f"Retrieved {len(entities)} {self.model.__name__}(s)")
            return entities
        except Exception as e:
            logger.exception(f"Error fetching all {self.model.__name__}: {e}")
            raise

    async def get_by_field(self, field_name: str, value: Any) -> list[ModelType]:
        logger.debug(f"Fetching {self.model.__name__} by {field_name}={value}")
        stmt = select(self.model).filter(getattr(self.model, field_name) == value)

        try:
            result = await self.db.execute(stmt)
            entities = result.unique().scalars().all()
            logger.debug(
                f"Retrieved {len(entities)} {self.model.__name__}(s) \
                    matching {field_name}={value}"
            )
            return entities
        except Exception as e:
            logger.exception(
                f"Error fetching {self.model.__name__} by {field_name}={value}: {e}"
            )
            raise

    async def update(self, updated_obj: ModelType) -> ModelType:
        logger.debug(f"Updating {self.model.__name__} with data: {updated_obj}")
        try:
            self.db.add(updated_obj)
            await self.db.commit()
            await self.db.refresh(updated_obj)
            logger.debug(
                f"{self.model.__name__} with ID {updated_obj.id} updated successfully"
            )
            return updated_obj
        except Exception as e:
            logger.exception(
                f"Error updating {self.model.__name__} with ID {updated_obj.id}: {e}"
            )
            raise

    async def delete(self, object_id: int) -> bool:
        logger.debug(f"Deleting {self.model.__name__} with ID: {object_id}")
        obj = await self.get_by_id(object_id)
        if not obj:
            logger.warning(f"{self.model.__name__} with ID {object_id} not found")
            return False
        try:
            await self.db.delete(obj)
            await self.db.commit()
            logger.debug(
                f"{self.model.__name__} with ID {object_id} deleted successfully"
            )
            return True
        except Exception as exc:
            logger.exception(
                f"Error deleting {self.model.__name__} with ID {object_id}: {exc}"
            )
            raise
