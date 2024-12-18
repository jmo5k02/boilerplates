import logging
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.requests import Request

from app.tenants.service import TenantService
from app.tenants.schemas import TenantRead
from app.auth.deps import get_current_user, reusable_oauth2
from app.common.utils.enums import UserRoles

log = logging.getLogger(__name__)


async def any_permission(permissions: list["BasePermission"], request: Request):
    for p_class in permissions:
        try:
            p = p_class()
            await p(request=request)
            return True
        except HTTPException:
            pass
    return False


class BasePermission(ABC):
    """
    Abstract permission that all other permissions must be inherited from.

    Defines basic error message, status & error codes.

    At initialization, calls abstract method `has_required_permissions`
    which will be specific to concrete impolmeentation of Permission class.

    You would wirte your permissions like this:

    ```python
    class MozillaUserAgentPermission(BasePermission):
        async def has_required_permissions(self, request: Request):
            return request.headers.get('User-Agent') == "Mozilla/5.0")
    ```
    """

    tenant_error_msg = [{"msg": "Tenant not found. Please, contact admin"}]
    tenant_error_code = status.HTTP_404_NOT_FOUND

    user_error_msg = [{"msg": "User not found. Please, contact admin"}]
    user_error_code = status.HTTP_404_NOT_FOUND

    user_role_error_msg = [
        {
            "msg": "Your user doesn't have permissions to create, update, or delete this resource. Please, contact admin"
        }
    ]
    user_role_error_code = status.HTTP_403_FORBIDDEN

    role = None
    is_superuser = False

    @abstractmethod
    async def has_required_permissions(self, request: Request) -> bool: ...

    async def __call__(self, request: Request):
        tenant = None
        _tenant_service = TenantService(request.state.db)
        if request.path_params.get("tenant"):
            tenant = await _tenant_service.get_by_slug_or_raise(
                tenant_in=TenantRead(
                    name=request.path_params.get("tenant"),
                    slug=request.path_params.get("tenant"),
                )
            )
        elif request.query_params.get("tenant_id"):
            tenant = await _tenant_service.get(id=request.query_params.get("tenant_id"))

        if not tenant:
            raise HTTPException(
                status_code=self.tenant_error_code, detail=self.tenant_error_msg
            )

        user = await get_current_user(request)
        if not user:
            raise HTTPException(
                status_code=self.user_error_code, detail=self.user_error_msg
            )

        self.role = user.get_tenant_role(tenant.slug)
        self.is_superuser = user.is_superuser()
        print(self.role)
        if not await self.has_required_permissions(request):
            raise HTTPException(
                status_code=self.user_role_error_code, detail=self.user_role_error_msg
            )


class PermissionsDependency(object):
    """
    Permission dependency that is used to define and check all the permission
    classes from one place inside route definition

    Use it as an argument to FastAPI's `Depends` as follows:

    ```python
    app = FastAPI()

    @app.get(
        "/mozilla/",
        dependencies=[Depends(
            PermissionsDependency([MozillaUserAgentPermission]))]
    )
    async def mozilla() -> dict:
        return {"mozilla": True}
    ```
    """

    def __init__(self, permission_classes: list[BasePermission]):
        self.permission_classes = permission_classes

    async def __call__(self, request: Request):
        for permission_class in self.permission_classes:
            p = permission_class()
            await p(request=request)


class SuperUserPermission(BasePermission):
    async def has_required_permissions(self, request: Request) -> bool:
        return self.is_superuser
    

class TenantOwnerPermission(BasePermission):
    async def has_required_permissions(self, request: Request) -> bool:
        return self.role == UserRoles.owner

class TenantManagerPermission(BasePermission):
    async def has_required_permissions(self, request: Request) -> bool:
        permission = await any_permission(
            permissions=[
                TenantOwnerPermission,
            ],
            request=request,
        )
        if not permission:
            if self.role == UserRoles.manager:
                return True
        return permission
    
class TenantAdminPermission(BasePermission):
    async def has_required_permissions(self, request: Request) -> bool:
        permission = await any_permission(
            permissions=[
                TenantOwnerPermission,
                TenantManagerPermission,
            ],
            request=request,
        )
        if not permission:
            if self.role == UserRoles.admin:
                return True
        return permission


class TenantMemberPermission(BasePermission):
    async def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        permission = await any_permission(
            permissions=[
                TenantOwnerPermission,
                TenantManagerPermission,
                TenantAdminPermission,
            ],
            request=request,
        )
        if not permission:
            if self.role == UserRoles.member:
                return True
        return permission