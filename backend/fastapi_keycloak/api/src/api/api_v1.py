from fastapi import APIRouter

from src.users import router as user_router
from src.auth.router import router as auth_router

router = APIRouter()

## User routes
router.include_router(user_router.router, prefix="/users", tags=["users"])

## Auth routes
router.include_router(auth_router, prefix="/auth", tags=["auth"])