from fastapi import APIRouter, Depends

from app.deps import SettingsDep

router = APIRouter()

@router.get("/health", status_code=200)
async def get_health(settings: SettingsDep):
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "testing": settings.testing
    }
