from pydantic import BaseModel, UUID4

class SummaryBase(BaseModel):
    url: str

class SummaryCreate(SummaryBase):
    pass

class SummaryUpdate(SummaryBase):
    pass

class SummaryOutput(SummaryBase):
    id: UUID4
    summary: str

