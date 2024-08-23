from fastapi import APIRouter

from src.users import router as user_router
from src.auth import router as auth_router
from src.emails import router as email_router

router = APIRouter()

## User routes
router.include_router(user_router.router, prefix="/users", tags=["users"])

## Auth routes
router.include_router(auth_router.router, prefix="/auth", tags=["auth"])

## Email routes
router.include_router(email_router.router, prefix="/emails", tags=["emails"])