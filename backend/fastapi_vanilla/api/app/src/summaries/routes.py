import logging
from fastapi import APIRouter, Depends

from app.deps import DbSessionDep
from .model import Summary
from .schemas import SummaryCreate, SummaryOutput

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=SummaryOutput, status_code=201)
async def create_summary(session: DbSessionDep,
                   summary: SummaryCreate
                   ) -> SummaryOutput:
    logger.info("Got request to create summary: %s", summary)
    summary = Summary(
        url=summary.url,
        summary="This is a dummy summary"
    )
    session.add(summary)
    await session.commit()
    await session.refresh(summary)
    return SummaryOutput(**summary.__dict__)