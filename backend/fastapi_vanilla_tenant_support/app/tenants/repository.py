from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_repository import BaseRepository
from app.tenants.models import Tenant

class TenantRepository(BaseRepository[Tenant]):
    def __init__(self, session: AsyncSession):
        super().__init__(Tenant, session)