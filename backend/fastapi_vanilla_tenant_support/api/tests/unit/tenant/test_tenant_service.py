import pytest
import time
from slugify import slugify

from app.tenants.service import TenantService
from app.tenants.schemas import TenantCreate, TenantUpdate
from app.common.utils.sqlalchemy_utils import database_exists

from tests.conftest import settings


@pytest.mark.anyio
async def test_get_tenant(tenant, session):
    _service = TenantService(session)
    tenant = await _service.get_by_name(tenant.name)
    print("##############################################")
    print(tenant.name)
    print(tenant.slug)
    print(tenant.id)
    # print(tenant.users)
    print("##############################################")
    assert tenant is not None


@pytest.mark.anyio
async def test_get_all_tenants(tenant, session):
    _service = TenantService(session)
    tenants = await _service.get_all()
    tenants = list(tenants)
    te = [t.dict() for t in tenants]
    print(te)
    assert len(tenants) > 0


@pytest.mark.anyio
async def test_create_tenant(session):
    _service = TenantService(session)
    tenant_in = TenantCreate(
        name="Test Tenant",
        description="Test Tenant Description",
        default=False,
    )
    tenant = await _service.create(tenant_in)
    assert tenant
    

@pytest.mark.anyio
async def test_update_tenant(tenant, session):
    _service = TenantService(session)
    tenant = await _service.get_by_name(tenant.name)
    update_name = "Test Tenant Updated"
    update_description = "Test Tenant Description Updated"
    update_default = False
    tenant_in = TenantUpdate(
        id=tenant.id,
        name=update_name,
        description=update_description,
        default=update_default,
    )
    new_tenant = await _service.update(tenant=tenant, obj_in=tenant_in)
    assert new_tenant.name == tenant.name, tenant.__dict__ # name should not change
    assert new_tenant.description == update_description, tenant.__dict__
    assert new_tenant.default == update_default, tenant.__dict__


@pytest.mark.anyio
async def test_delete_tenant(tenant, session):
    _service = TenantService(session)
    await _service.delete(tenant.id)
    tenant = await _service.get_by_name(tenant.name)
    assert tenant is None




# @pytest.mark.anyio
# async def test_add_user_to_tenant(user_tenant, session):
#     _service = TenantService(session)
#     tenant = await _service.get_by_name(user_tenant[1].name)
#     user = await _service.add_user(tenant=tenant, user=user_tenant[0], role=user_tenant[0].get_tenant_role(tenant.slug))
#     assert user is not None
    