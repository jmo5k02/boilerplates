import logging
from sqlalchemy.orm import Session
from pydantic import UUID4
from fastapi import APIRouter

from src.api_core.deps import DbSession
from .schema import UserCreate, UserOutput
from .models import User

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def create_user(self,
                    data: UserCreate,
                    kc_user_id: UUID4
                    ) -> User|None:
        logger.info("Creating user with email '%s'", data)
        user = User(
            **data.model_dump(exclude=["password"]),
            id=UUID4(str(kc_user_id))
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
