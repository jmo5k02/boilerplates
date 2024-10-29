from pydantic import BaseModel
from fastapi import APIRouter, Depends

from app.auth.routes import user_router, auth_router
from app.db.deps import get_tenant_session

class ErrorMessage(BaseModel):
    msg: str


class ErrorResponse(BaseModel):
    error: ErrorMessage


api_router = APIRouter(
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)

api_router.include_router(auth_router, prefix="/{tenant}/auth", tags=["auth"])


# All routes that require an authenticated user should be in this router
authenticated_user_api_router = APIRouter()

# All routes that require an authenticated tenant should be in this router
authenticated_tenant_api_router = APIRouter(
    prefix="/{tenant}", dependencies=[Depends(get_tenant_session)]
)

authenticated_tenant_api_router.include_router(
    user_router, prefix="/users", tags=["users"]
)


api_router.include_router(authenticated_user_api_router)

api_router.include_router(authenticated_tenant_api_router)
