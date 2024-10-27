from pydantic import UUID4, BaseModel, HttpUrl


class SummaryBase(BaseModel):
    url: HttpUrl


class SummaryCreate(SummaryBase):
    pass


class SummaryUpdate(SummaryBase):
    pass


class SummaryOutput(SummaryBase):
    id: UUID4
    summary: str
