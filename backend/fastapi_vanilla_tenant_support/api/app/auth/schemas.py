from typing import Optional
from pydantic import EmailStr, Field, UUID4

from app.common.utils.base_classes.base_schema import AppBaseSchema
from app.tenants.schemas import TenantRead
from app.common.utils.enums import UserRoles


class UserTenant(AppBaseSchema):
    tenant: TenantRead
    default: Optional[bool] = Field(None, nullable=True)
    role: Optional[UserRoles] = Field(None, nullable=True)


class UserBase(AppBaseSchema):
    email: EmailStr
    tenant_associations: Optional[list[UserTenant]] = []


class UserLogin(UserBase):
    password: str


class UserRegister(UserLogin):
    pass


class UserLoginResponse(AppBaseSchema):
    token: Optional[str] = Field(None, nullable=True)


class UserRead(UserBase):
    id: UUID4
    role: Optional[UserRoles] = Field(None, nullable=True)


class UserUpdate(AppBaseSchema):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    tenants: Optional[list[TenantRead]] = []
    role: Optional[UserRoles] = Field(None, nullable=True)


class UserCreate(AppBaseSchema):
    email: EmailStr
    password: str
    tenants: Optional[list[TenantRead]] = []
    role: Optional[UserRoles] = Field(None, nullable=True)


class UserRegisterResponse(AppBaseSchema):
    token: Optional[str] = Field(None, nullable=True)


class UserTokenData(AppBaseSchema):
    email: EmailStr
