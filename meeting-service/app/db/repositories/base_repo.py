from typing import Any, Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_by_id(self, id: int) -> ModelType:
        stmt = select(self.model).filter(self.model.id == id)

        # Add eager loading for common relationships if applicable
        if hasattr(self.model, "attendees"):
            stmt = stmt.options(joinedload(self.model.attendees))
        if hasattr(self.model, "recurrence"):
            stmt = stmt.options(joinedload(self.model.recurrence))

        result = await self.db.execute(stmt)
        return result.unique().scalar()

    async def get_all(self, skip: int = 0, limit: int = 10) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)

        # Add eager loading for relationships if applicable
        if hasattr(self.model, "attendees"):
            stmt = stmt.options(joinedload(self.model.attendees))
        if hasattr(self.model, "recurrence"):
            stmt = stmt.options(joinedload(self.model.recurrence))

        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_by_field(self, field_name: str, value: Any) -> list[ModelType]:
        stmt = select(self.model).filter(getattr(self.model, field_name) == value)

        # Add eager loading for common relationships if applicable
        if hasattr(self.model, "attendees"):
            stmt = stmt.options(joinedload(self.model.attendees))
        if hasattr(self.model, "recurrence"):
            stmt = stmt.options(joinedload(self.model.recurrence))

        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def update(self, id: int, update_data: dict) -> ModelType:
        obj = await self.get_by_id(id)
        if not obj:
            return None
        for key, value in update_data.items():
            setattr(obj, key, value)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: int) -> bool:
        obj = await self.get_by_id(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
            return True
        return False
