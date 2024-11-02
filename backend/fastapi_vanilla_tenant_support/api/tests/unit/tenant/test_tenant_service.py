import pytest

from app.tenants.service import TenantService

@pytest.mark.anyio
async def test_get_tenant(tenant, session):
    _service = TenantService(session)
    tenant = await _service.get_by_name(tenant.name)
    print(tenant._repr_attrs_str)
    assert tenant is not None

@pytest.mark.anyio
async def test_get_all_tenants(tenant, session):
    _service = TenantService(session)
    tenants = await _service.get_all()
    assert len(tenants) > 0