from fastapi import APIRouter, Depends, HTTPException, status

from app.tenants.schemas import TenantCreate, TenantRead, TenantUpdate


router = APIRouter()


@router.get("", response_model=list[TenantRead])
async def get_organizations():
    """
    Get all tenants
    """
    pass


@router.post("", response_model=TenantRead)
async def create_tenant(data: TenantCreate):
    """
    Create a new tenant
    """
    pass


@router.get("/{tenant_id}", response_model=TenantRead)
async def get_tenant_by_id(tenant_id: int):
    """
    Get a tenant by ID
    """
    pass


@router.put(
    "/{tenant_id}",
    response_model=TenantRead,
    dependencies=[Depends()]
)
async def update_tenant(tenant_id: int, data: TenantUpdate):
    """
    Update a tenant by ID
    """
    pass