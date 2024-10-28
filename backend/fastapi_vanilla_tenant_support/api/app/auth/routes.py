from sqlalchemy import select
from fastapi import APIRouter, Depends, status

from app.db.deps import TenantDbSessionDep
from app.auth.permissions import TenantOwnerPermission, PermissionsDependency
from app.auth.models import AppUser
from app.auth.schemas import UserCreate, UserRead
from .service import AuthService

auth_router = APIRouter()
user_router = APIRouter()


@user_router.get(
    "", dependencies=[Depends(PermissionsDependency([TenantOwnerPermission]))]
)
async def get_all_users(tenant: str, session: TenantDbSessionDep):
    """Get all users for a tenant"""
    print(session)
    query = select(AppUser)
    users = await session.execute(query)
    users = users.all()
    print(users)
    return users

@user_router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, ):
    """Create a user"""
    pass