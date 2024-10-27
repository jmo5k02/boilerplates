import logging
from abc import ABC, abstractmethod

from fastapi import HTTPException, status
from fastapi.requests import Request

from app.tenants.service import TenantService

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

    ten_error_msg = [{"msg": "Tenant not found. Please, contact admin"}]
    ten_error_code = status.HTTP_404_NOT_FOUND

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
    def has_required_permissions(self, request: Request) -> bool: ...

    def __init__(self, request: Request):
        tenant = None
        if request.path_params.get("tenant"):
            tenant = TenantService
        

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

        