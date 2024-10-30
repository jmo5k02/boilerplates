from sqlalchemy.ext.asyncio import AsyncSession

from app.common.utils.base_classes.base_repository import BaseRepository

from app.auth.models import AppUser

class AuthRepository(BaseRepository[AppUser]):
    def __init__(self, session: AsyncSession):
        super().__init__(AppUser, session) 