from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4

from app.utils.base_classes.base_service import BaseService
from app.utils.enums import UserRoles
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
from app.tenants.service import TenantService
from app.tenants.schemas import TenantRead


class AuthService(BaseService[AppUser, UserCreate, UserUpdate, UserRead]):
    def __init__(self, session: AsyncSession):
        super().__init__(AuthRepository, session)
        self.tenant_service = TenantService(session)
        self.session = session

    async def create_user(self, tenant: str, user_in: UserCreate) -> UserRead:
        """Creates new user"""
        password = bytes(user_in.password, "utf-8")

        user = AppUser(
            **user_in.model_dump(exclude={"password", "tenants", "role"}),
            password=password
        )

        tenant = await self.tenant_service.get_by_slug_or_raise(
            tenant_in = TenantRead(name=tenant, slug=tenant)
        )

        role = UserRoles.member
        if hasattr(user_in, "role"):
            role = user_in.role
        
        user.tenants.append(AppUserTenant(tenant=tenant, role=role))

        await self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_email(self, email: str) -> UserRead:
        """Returns user by email"""
        user = await self.repository.get_by_email(email)
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
