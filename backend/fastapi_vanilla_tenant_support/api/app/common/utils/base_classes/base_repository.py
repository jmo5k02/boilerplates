"""
This module contains the base repository class that all repositories should inherit from.
"""
from typing import Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import Base
from app.common.utils.base_classes.base_schema import AppBaseSchema


DatabaseModelType = TypeVar('DatabaseModelType', bound=Base) # type: ignore
CreateSchemaType = TypeVar('CreateSchemaType', bound=AppBaseSchema)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=AppBaseSchema)

class BaseRepository(Generic[DatabaseModelType]):
    """
    This class is the base repository class that all repositories should inherit from.
    Args:
      model (Type[DatabaseModelType]): The database model class that the repository will be working with. 
        You HAVE TO pass a model that inherits from the Base class in the database module.
      session (AsyncSession): The database session that the repository will be working with.
    Examples:
    ```python
    class AvailableModelRepository(BaseRepository[AvailableModel]):
        def __init__(self, session: Session):
            super().__init__(AvailableModel, session)
    ```
    """
    def __init__(self, model: Type[DatabaseModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, obj_in: CreateSchemaType) -> DatabaseModelType:
        db_obj = self.model(**obj_in.model_dump())
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get(self, id: int) -> DatabaseModelType:
        query = select(self.model).where(self.model.id == id)
        obj = await self.session.execute(query)
        return obj.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[DatabaseModelType]:
        query = select(self.model).offset(skip).limit(limit)
        objects = await self.session.execute(query)
        return objects.scalars().all()

    async def update(self,id: int, obj_in: UpdateSchemaType) -> DatabaseModelType:
        db_obj = await self.get(id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            self.session.commit()
            self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        obj = await self.get(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False