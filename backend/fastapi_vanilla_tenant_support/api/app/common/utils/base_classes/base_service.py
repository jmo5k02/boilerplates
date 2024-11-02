"""
This module contains the base service class that all services should inherit from.
"""

from typing import Generic, TypeVar, Type
from pydantic import BaseModel, UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from app.db.base import Base
from .base_repository import BaseRepository


DatabaseModelType = TypeVar("DatabaseModelType", bound=Base) # type: ignore
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
OutputSchemaType = TypeVar("OutputSchemaType", bound=BaseModel)


class BaseService(
    Generic[DatabaseModelType, CreateSchemaType, UpdateSchemaType, OutputSchemaType]
):
    """
    Base service class providing common CRUD operations with generic type support.
    
    This class serves as a foundation for all service classes in the application,
    implementing common database operations while maintaining type safety through
    generics.

    Type Parameters:
    ----------------
        DatabaseModelType (Base): The SQLAlchemy model class for the database entity
        CreateSchemaType (BaseModel): Pydantic model for create operations (must inherit from BaseModel)
        UpdateSchemaType (BaseModel): Pydantic model for update operations (must inherit from BaseModel)
        OutputSchemaType (BaseModel): Pydantic model for response/output data (must inherit from BaseModel)

    Attributes:
        repository (BaseRepository): The repository class that the service will be working with.
        session (Session): The database session that the service will be working with.
        
    Example:
        ```python
        class AvailableModelService(
            BaseService[
                AvailableModel, 
                AvailableModelCreate, 
                AvailableModelUpdate, 
                AvailableModelOutput
            ]
        ):
            def __init__(self, session: Session):
                super().__init__(AvailableModelRepository, session)
        ```
    Note:
        - All schema types must be Pydantic models (inherit from BaseModel)
        - The repository must implement the BaseRepository interface
        - Services inheriting from this class should specify all four type parameters
    """
    obj_not_found_error = HTTPException(status_code=404, detail=f"{DatabaseModelType.__name__} not found")

    def __init__(self, repository: BaseRepository, session: AsyncSession):
        self.repository: BaseRepository = repository(session)
        self.output_schema: Type[OutputSchemaType] = self.__orig_bases__[0].__args__[3]

    async def create(self, obj_in: CreateSchemaType) -> OutputSchemaType:
        try:
            created_obj = await self.repository.create(obj_in)
            return self.output_schema(**created_obj.__dict__)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=400, detail=f"Create operation failed: {str(e)}"
            )

    async def get(self, id: UUID4) -> OutputSchemaType:
        obj = await self.repository.get(id)
        if not obj:
            raise self.obj_not_found_error
        return obj

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[OutputSchemaType]:
        all_objs = await self.repository.get_all(skip, limit)
        return all_objs

    async def update(self, id: UUID4, obj_in: UpdateSchemaType) -> OutputSchemaType:
        obj = await self.repository.update(id, obj_in)
        if not obj:
            raise self.obj_not_found_error
        return self.output_schema(**obj.__dict__)

    async def delete(self, id: UUID4) -> bool:
        if not await self.repository.delete(id):
            raise self.obj_not_found_error
        return True