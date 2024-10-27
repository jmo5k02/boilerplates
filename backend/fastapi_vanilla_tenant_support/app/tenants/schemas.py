from typing import Optional
from pydantic import UUID4, Field

from app.core.base_schema import CustomBaseSchema

class TenantBase(CustomBaseSchema):
    name: str
    description: str
    default: bool


class TenantCreate(TenantBase):
    pass


class TenantUpdate(CustomBaseSchema):
    id: Optional[UUID4]
    description: Optional[str] = Field(None, nullable=True)
    default: Optional[bool] = Field(False, nullable=True)

class TenantRead(TenantBase):
    id: UUID4
    slug: str

