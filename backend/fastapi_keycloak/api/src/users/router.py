"""
This is the main router for the user resource.  
Here all routes for interacting with the user resource are defined.
"""
import logging
from pydantic import UUID4
from fastapi import APIRouter

from src.api_core.deps import DbSession
from .schema import UserCreate, UserOutput
from .service import UserService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/all")
async def get_all_users(session: DbSession):
    raise NotImplementedError


@router.get("/{user_id}")
async def get_user_by_id(session: DbSession,
                   user_id: UUID4):
    raise NotImplementedError


@router.post("/", status_code=201, response_model=UserOutput)
async def create_user(session: DbSession,
                data: UserCreate):
    # This could i.e. be used by and admin to create users
    raise NotImplementedError

@router.put("/{user_id}")
async def update_user():
    raise NotImplementedError


