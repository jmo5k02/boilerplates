import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from typing import Optional
from pydantic import UUID4

from app.common.utils.base_classes.base_service import BaseService
from app.common.utils.enums import UserRoles
from app.auth.models import AppUser, AppUserTenant
from app.auth.repository import AuthRepository
from app.auth.schemas import (
    UserCreate,
    UserRegister,
    UserUpdate,
    UserRead,
    UserLoginResponse,
    UserLogin,
    UserTenant,
)
from app.auth.utils import create_access_token, get_password_hash
from app.tenants.service import TenantService
from app.tenants.schemas import TenantRead


class AuthService(BaseService[AppUser, UserCreate, UserUpdate, UserRead]):
    def __init__(self, session: AsyncSession):
        super().__init__(AuthRepository, session)
        self.tenant_service = TenantService(session)
        self.session = session

    async def get_all_tenant_users(self, tenant: str) -> list[AppUser]:
        """Get all users for a tenant"""
        query = (
            select(AppUser)
            .join(AppUser.tenants)
            .join(AppUserTenant.tenant)
            .filter(AppUserTenant.tenant.has(slug=tenant))
        )
        users = await self.session.execute(query)
        return users.scalars().all()
    
    async def get(self, user_id: UUID4) -> Optional[AppUser]:
        """Get a user"""
        user = await self.session.execute(select(AppUser).filter(AppUser.id == user_id))
        return user.scalar()
    
    async def get_or_raise(self, user_id: UUID4) -> AppUser:
        """Get a user or raise"""
        user = await self.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def create_user(self, tenant: str, user_in: UserCreate) -> AppUser:
        """Creates new user"""
        password = bytes(user_in.password, "utf-8")
        salt = secrets.token_bytes(32)

        salted_password = password + salt

        user = AppUser(
            **user_in.model_dump(exclude={"password", "tenants", "role"}),
            password=get_password_hash(salted_password),
            salt=salt,
        )

        tenant = await self.tenant_service.get_by_slug_or_raise(
            tenant_in = TenantRead(name=tenant, slug=tenant)
        )

        role = UserRoles.member
        if hasattr(user_in, "role"):
            role = user_in.role
        
        user.tenants.append(AppUserTenant(tenant=tenant, role=role))

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def create_user_or_raise(self, tenant: str, user_in: UserCreate) -> AppUser:
        """Creates new user or raises"""
        user = await self.get_by_email(user_in.email)
        if user:
            raise HTTPException(status_code=400, detail="User already exists")
        user = await self.create_user(tenant, user_in)
        # await self.session.refresh(user, ['tenants'])
        return user

    async def get_by_email(self, email: str) -> Optional[AppUser]:
        """Returns user by email"""
        user = await self.session.execute(select(AppUser).filter(AppUser.email == email))
        user = user.scalar_one_or_none()
        return user

    async def create_or_update_tenant_role(self, user: AppUser, role_in: UserTenant):
        """Creates or updates tenant role"""
        if not role_in.tenant.id:
            tenant = await self.tenant_service.get_by_name(name=role_in.tenant.name)
            tenant_id = tenant.id
        else:
            tenant_id = role_in.tenant.id

        tenant_role_query = (
            select(AppUserTenant)
            .filter(AppUserTenant.user_id == user.id)
            .filter(AppUserTenant.tenant_id == tenant_id)
        )
        tenant_role = await self.session.execute(tenant_role_query)
        tenant_role = tenant_role.scalar_one_or_none()

        if not tenant_role:
            return AppUserTenant(
                tenant_id=tenant_id,
                role=role_in.role,
            )

        tenant_role.role = role_in.role
        return tenant_role


    async def login_access_token(self, tenant: str, user_in: UserLogin) -> UserLoginResponse:
        """Logs in and returns access token"""
        user = await self.get_by_email(user_in.email)
        if user and user.check_password(user_in.password):
            return UserLoginResponse(token=user.token)