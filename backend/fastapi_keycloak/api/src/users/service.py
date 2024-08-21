import logging
from sqlalchemy.orm import Session
from pydantic import UUID4
from fastapi import APIRouter

from src.api.deps import DbSession
from .schema import UserCreate, UserOutput
from .repository import UserRepository


logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = UserRepository(session)

    async def create_user(self, 
                    data: UserCreate,
                    kc_user_id: UUID4
                    ) -> UserOutput|None:
        user = await self.repo.create_user(data, kc_user_id)
        return UserOutput(**user.__dict__)