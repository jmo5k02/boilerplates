from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from app.tenants.schemas import TenantCreate, TenantRead, TenantUpdate
from app.tenants.service import TenantService
from app.db.deps import DbSessionDep
from app.auth.deps import CurrentUserDep
from app.auth.permissions import (
    PermissionsDependency,
    SuperUserPermission,
    TenantOwnerPermission,
    TenantMemberPermission,
)
from app.common.utils.enums import UserRoles


router = APIRouter()


@router.get(
    "",
    response_model=list[TenantRead],
    dependencies=[Depends(PermissionsDependency([SuperUserPermission]))],
)
async def get_organizations(session: DbSessionDep, current_user: CurrentUserDep):
    """
    Get all tenants
    """
    _service = TenantService(session)
    tenants = await _service.get_all()
    return tenants


@router.post("", response_model=TenantRead)
async def create_tenant(
    session: DbSessionDep, current_user: CurrentUserDep, data: TenantCreate
):
    """
    Create a new tenant
    """
    _service = TenantService(session)
    tenant = await _service.get_by_name(data.name)
    if tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this name already exists",
        )
    tenant = await _service.create(data)

    _service.add_user(tenant=tenant, user=current_user, role=UserRoles.owner)

    return tenant


@router.get(
    "/{tenant_id}",
    response_model=TenantRead,
    dependencies=Depends(PermissionsDependency([TenantMemberPermission])),
)
async def get_tenant_by_id(tenant_id: UUID4):
    """
    Get a tenant by ID
    """
    pass


@router.put(
    "/{tenant_id}",
    response_model=TenantRead,
    dependencies=[Depends(PermissionsDependency([TenantOwnerPermission]))],
)
async def update_tenant(tenant_id: int, data: TenantUpdate):
    """
    Update a tenant by ID
    """
    pass
