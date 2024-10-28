from pydantic import BaseModel
from fastapi import APIRouter

from app.auth.routes import user_router, auth_router

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

api_router.include_router(user_router, prefix="/{tenant}/users", tags=["users"])

# All routes that require an authenticated user should be in this router
authenticated_user_api_router = APIRouter()

# All routes that require an authenticated tenant should be in this router
authenticated_tenant_api_router = APIRouter()

