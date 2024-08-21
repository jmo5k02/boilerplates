from pydantic import BaseModel, UUID4


class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    address: str


class UserCreate(UserBase):
    password: str



class UserOutput(UserBase):
    id: UUID4