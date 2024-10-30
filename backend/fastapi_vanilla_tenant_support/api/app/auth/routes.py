import asyncio
from sqlalchemy import select
from fastapi import APIRouter, Depends, status, Request

from app.db.deps import DbSessionDep, get_tenant_session
from app.auth.permissions import (
    TenantOwnerPermission,
    TenantMemberPermission,
    PermissionsDependency,
)
from app.auth.models import AppUser
from app.auth.schemas import (
    UserCreate,
    UserRead,
    UserLogin,
    UserLoginResponse,
    UserRegisterResponse,
)
from .service import AuthService

auth_router = APIRouter(dependencies=[Depends(get_tenant_session)])
user_router = APIRouter()


@user_router.get(
    "", dependencies=[Depends(PermissionsDependency([TenantMemberPermission]))], response_model=list[UserRead]
)
async def get_all_users(request: Request, session: DbSessionDep):
    """Get all users for a tenant"""
    _service = AuthService(session)
    return {"message": "Get all users"}


@user_router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
):
    """Create a user"""
    pass


@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int):
    """Get a user"""
    pass


@user_router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user_in: UserCreate):
    """Update a user"""
    pass


@auth_router.get("/me", response_model=UserRead)
async def get_current_user():
    """Get current user"""
    pass


@auth_router.get("/myrole")
async def get_current_user_role():
    """Get current user role"""
    pass


@auth_router.post("/login/access-token", response_model=UserLoginResponse)
async def login_access_token(user_in: UserLogin, tenant: str, session: DbSessionDep):
    """Login and return access token"""
    _service = AuthService(session)
    return await _service.login_access_token(tenant, user_in)


@auth_router.post("/register", response_model=UserRead)
async def register(user_in: UserCreate, tenant: str, session: DbSessionDep):
    """Register a user"""
    _service = AuthService(session)
    user: AppUser = await _service.create_user_or_raise(tenant, user_in)
    return user
