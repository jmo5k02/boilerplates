from typing import Optional
from pydantic import UUID4, Field

from app.utils.base_classes.base_schema import AppBaseSchema

class TenantBase(AppBaseSchema):
    name: str
    description: str
    default: bool


class TenantCreate(TenantBase):
    pass


class TenantUpdate(AppBaseSchema):
    id: Optional[UUID4]
    description: Optional[str] = Field(None, nullable=True)
    default: Optional[bool] = Field(False, nullable=True)

class TenantRead(TenantBase):
    id: UUID4
    slug: str

