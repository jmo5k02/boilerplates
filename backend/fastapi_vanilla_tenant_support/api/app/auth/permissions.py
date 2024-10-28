import logging
from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from fastapi.requests import Request

from app.tenants.service import TenantService
from app.tenants.schemas import TenantRead

log = logging.getLogger(__name__)


def any_permission(permissions: list, request: Request):
    for p in permissions:
        try:
            p(request=request)
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
        def has_required_permissions(self, request: Request):
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

    @abstractmethod
    async def has_required_permissions(self, request: Request) -> bool: ...

    async def __call__(self, request: Request, tenant_service: TenantService):
        tenant = None
        if request.path_params.get("tenant"):
            tenant = await tenant_service.get_by_slug_or_raise(
                tenant_in=TenantRead(
                    name=request.path_params.get("tenant"),
                    slug=request.path_params.get("tenant"),
                )
            )
        elif request.query_params.get("tenant_id"):
            tenant = await tenant_service.get(id=request.query_params.get("tenant_id"))

        if not tenant:
            raise HTTPException(
                status_code=self.tenant_error_code, detail=self.tenant_error_msg
            )

        user = get_current_user(request)
        if not user:
            raise HTTPException(
                status_code=self.user_error_code, detail=self.user_error_msg
            )

        self.role = user.get_tenant_role(tenant.slug)
        if not self.has_required_permissions(request):
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

    def __init__(self, permission_classes: list):
        self.permission_classes = permission_classes

    def __call__(self, request: Request):
        for permission_class in self.permission_classes:
            permission_class(request=request)


class TenantOwnerPermission(BasePermission):
    async def has_required_permissions(self, request: Request) -> bool:
        pass
