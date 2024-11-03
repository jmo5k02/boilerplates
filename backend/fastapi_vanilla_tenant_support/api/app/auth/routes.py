import asyncio
from sqlalchemy import select
from pydantic import UUID4
from fastapi import APIRouter, Depends, status, Request, HTTPException

from app.db.deps import DbSessionDep, get_tenant_session, CommonParametersDep
from app.common.utils.enums import UserRoles
from app.auth.deps import CurrentUserRoleDep, CurrentUserDep
from app.auth.permissions import (
    TenantOwnerPermission,
    TenantAdminPermission,
    TenantManagerPermission,
    TenantMemberPermission,
    PermissionsDependency,
)
from app.auth.models import AppUser
from app.auth.schemas import (
    UserCreate,
    UserRead,
    UserLogin,
    UserLoginResponse,
    UserUpdate,
    UserRegisterResponse,
)
from .service import AuthService

auth_router = APIRouter(dependencies=[Depends(get_tenant_session)])
user_router = APIRouter()


@user_router.get(
    "",
    dependencies=[Depends(PermissionsDependency([TenantMemberPermission]))],
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
)
async def get_all_users(tenant: str, session: DbSessionDep):
    """Get all users for a tenant"""
    _service = AuthService(session)
    users = await _service.get_all_tenant_users(tenant)
    return users


@user_router.post(
    "",
    dependencies=[Depends(PermissionsDependency([TenantOwnerPermission]))],
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_in: UserCreate,
    session: DbSessionDep,
):
    """Create a user"""
    _service = AuthService(session)
    user = await _service.get_by_email(user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists"
        )
    user = await _service.create_user(user_in)
    return user


@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID4, session: DbSessionDep):
    """Get a user"""
    _service = AuthService(session)
    user = await _service.get_or_raise(user_id=user_id)
    return user


@user_router.put(
    "/{user_id}",
    response_model=UserRead,
)
async def update_user(
    user_id: UUID4,
    user_in: UserUpdate,
    session: DbSessionDep,
    current_user: CurrentUserDep,
    tenant: str,
):
    """Update a user"""
    _service = AuthService(session)
    user = await _service.get_or_raise(user_id=user_id)
    current_user_tenant_role = current_user.get_tenant_role(tenant)
    user_is_owner = current_user_tenant_role == UserRoles.owner
    # The user himself can update his own user and Owner can update any user
    if user.id != current_user.id and not user_is_owner:
        raise HTTPException(status_code=403, detail="You can only update your own user")
    
    # Only the owner can update the user's role
    if user_in.role:
        if current_user_tenant_role != user_in.role:
            if not user_is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=[
                        {
                            "msg": "You don't have permissions to update the user's role. Please, contact the organization's owner."
                        }
                    ],
                )
    # TODO finish the update user logic
    user_in.tenants = []

    user = await _service.update(user, user_in)
    return user


@auth_router.get("/me", response_model=UserRead)
async def get_current_user(curent_user: CurrentUserDep):
    """Get current user"""
    print("curent_user", curent_user)
    print("curent_user", curent_user.__dict__)
    print("curent_user", curent_user.tenants[0].name)
    return curent_user


@auth_router.get("/myrole")
async def get_current_user_role(role: CurrentUserRoleDep):
    """Get current user role"""
    return {"role": role}


@auth_router.post("/login", response_model=UserLoginResponse)
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
