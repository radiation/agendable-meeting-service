from typing import Any, Generic, Type, TypeVar

from app.core.logging_config import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, obj_in: dict) -> ModelType:
        logger.debug(f"Creating {self.model.__name__} with data: {obj_in}")
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        try:
            await self.db.commit()
            await self.db.refresh(db_obj)
            logger.debug(
                f"{self.model.__name__} created successfully with ID: {db_obj.id}"
            )
            return db_obj
        except Exception as e:
            logger.exception(f"Error creating {self.model.__name__}: {e}")
            raise

    async def get_by_id(self, id: int) -> ModelType:
        logger.debug(f"Fetching {self.model.__name__} with ID: {id}")
        stmt = select(self.model).filter(self.model.id == id)

        if hasattr(self.model, "attendees"):
            stmt = stmt.options(joinedload(self.model.attendees))
        if hasattr(self.model, "recurrence"):
            stmt = stmt.options(joinedload(self.model.recurrence))

        try:
            result = await self.db.execute(stmt)
            entity = result.unique().scalar()
            if not entity:
                logger.warning(f"{self.model.__name__} with ID {id} not found")
            else:
                logger.debug(f"Retrieved {self.model.__name__}: {entity}")
            return entity
        except Exception as e:
            logger.exception(f"Error fetching {self.model.__name__} with ID {id}: {e}")
            raise

    async def get_all(self, skip: int = 0, limit: int = 10) -> list[ModelType]:
        logger.debug(
            f"Fetching all {self.model.__name__} with skip={skip}, limit={limit}"
        )
        stmt = select(self.model).offset(skip).limit(limit)

        if hasattr(self.model, "attendees"):
            stmt = stmt.options(joinedload(self.model.attendees))
        if hasattr(self.model, "recurrence"):
            stmt = stmt.options(joinedload(self.model.recurrence))

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

        if hasattr(self.model, "attendees"):
            stmt = stmt.options(joinedload(self.model.attendees))
        if hasattr(self.model, "recurrence"):
            stmt = stmt.options(joinedload(self.model.recurrence))

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

    async def update(self, id: int, update_data: dict) -> ModelType:
        logger.debug(
            f"Updating {self.model.__name__} with ID: {id} and data: {update_data}"
        )
        obj = await self.get_by_id(id)
        if not obj:
            logger.warning(f"{self.model.__name__} with ID {id} not found")
            return None
        try:
            for key, value in update_data.items():
                setattr(obj, key, value)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.debug(f"{self.model.__name__} with ID {id} updated successfully")
            return obj
        except Exception as e:
            logger.exception(f"Error updating {self.model.__name__} with ID {id}: {e}")
            raise

    async def delete(self, id: int) -> bool:
        logger.debug(f"Deleting {self.model.__name__} with ID: {id}")
        obj = await self.get_by_id(id)
        if not obj:
            logger.warning(f"{self.model.__name__} with ID {id} not found")
            return False
        try:
            await self.db.delete(obj)
            await self.db.commit()
            logger.debug(f"{self.model.__name__} with ID {id} deleted successfully")
            return True
        except Exception as e:
            logger.exception(f"Error deleting {self.model.__name__} with ID {id}: {e}")
            raise
