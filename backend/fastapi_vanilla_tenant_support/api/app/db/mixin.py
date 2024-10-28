import uuid
from datetime import datetime
from typing import TypeVar, Type, Optional

from pydantic import UUID4
from sqlalchemy import DateTime, event, select, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound="CustomBase")

class UUIDMixin(object):
    """UUID mixin"""
    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True, unique=True, default=uuid.uuid4)


class TimeStampMixin(object):
    """Timestamping mixin"""

    created_at = mapped_column(DateTime, default=datetime.utcnow)
    created_at._creation_order = 9998
    updated_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at._creation_order = 9998

    @staticmethod
    def _updated_at(mapper, connection, target):
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._updated_at)


class CrudMixin(object):
    """CRUD mixin"""
    @classmethod
    async def create(cls: Type[T], db: AsyncSession, **kwargs) -> T:
      obj = cls(**kwargs)
      db.add(obj)
      db.commit()
      db.refresh(obj)
      return obj

    @classmethod
    async def get_by_id(cls: Type[T], db: AsyncSession, id: UUID4) -> Optional[T]:
      query = select(cls).where(cls.id == id)
      result = await db.execute(query)
      return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls: Type[T], db: AsyncSession) -> list[T]:
      query = select(cls)
      result = await db.execute(query)
      return result.scalars().all()

    @classmethod
    async def update(cls: Type[T], db: AsyncSession, id: UUID4, **kwargs) -> Optional[T]:
      query = select(cls).where(cls.id == id)
      result = await db.execute(query)
      obj = result.scalar_one_or_none()
      if obj:
          for key, value in kwargs.items():
              setattr(obj, key, value)
          await db.commit()
          await db.refresh(obj)
      return obj

    @classmethod
    async def delete(cls: Type[T], db: AsyncSession, id: UUID4) -> bool:
      query = select(cls).where(cls.id == id)
      result = await db.execute(query)
      obj = result.scalar_one_or_none()
      if obj:
          await db.delete(obj)
          await db.commit()
          return True
      return False