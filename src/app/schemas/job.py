from pydantic import BaseModel


class Job(BaseModel):
    id: str


class JobRead(BaseModel):
    id: str
