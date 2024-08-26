import logging

from fastapi import APIRouter, HTTPException
from pydantic import UUID4
from sqlalchemy import select

from app.deps import DbSessionDep
from app.src.api_core.db.database import get_db

from .model import Summary
from .schemas import SummaryCreate, SummaryOutput

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=SummaryOutput, status_code=201)
async def create_summary(
    summary: SummaryCreate,
    session: DbSessionDep,
) -> SummaryOutput:
    logger.info("Got request to create summary: %s", summary)
    summary = Summary(url=str(summary.url), summary="This is a dummy summary")
    session.add(summary)
    await session.commit()
    await session.refresh(summary)
    return SummaryOutput(**summary.__dict__)


@router.get("/", response_model=list[SummaryOutput])
async def read_summaries(session: DbSessionDep) -> list[SummaryOutput]:
    logger.info("Got request to read all summaries")
    query = select(Summary)
    result = await session.execute(query)
    summaries = result.scalars().all()
    return [SummaryOutput(**summary.__dict__) for summary in summaries]


@router.get("/{summary_id}", response_model=SummaryOutput)
async def read_summary(
    summary_id: UUID4,
    session: DbSessionDep,
) -> SummaryOutput:
    logger.info("Got request to read summary with id: %s", summary_id)
    query = select(Summary).filter(Summary.id == summary_id)
    result = await session.execute(query)
    summary = result.scalar_one_or_none()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return SummaryOutput(**summary.__dict__)
