from fastapi import APIRouter

from app.src.summaries.routes import router as summaries_router

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

router.include_router(summaries_router, prefix="/summaries", tags=["summaries"])
