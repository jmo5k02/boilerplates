import pytest
import time
from app.tenants.service import TenantService

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
async def test_add_user_to_tenant(user_tenant, session):
    _service = TenantService(session)
    tenant = await _service.get_by_name(user_tenant[1].name)
    user = await _service.add_user(tenant=tenant, user=user_tenant[0], role=user_tenant[0].get_tenant_role(tenant.slug))
    assert user is not None
    