from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class ProgramBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100, examples=["12-Week Strength Program"])]
    description: Annotated[str | None, Field(max_length=1000, default=None)]
    duration_weeks: Annotated[int, Field(gt=0, examples=[12])]
    days_per_week: Annotated[int, Field(gt=0, le=7, examples=[4])]
    periodization_type: Annotated[str, Field(examples=["linear", "undulating", "block"])]
    is_public: Annotated[bool, Field(default=False)]
    is_active: Annotated[bool, Field(default=True)]


class ProgramCreate(ProgramBase):
    user_id: int | None = None


class ProgramUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    duration_weeks: int | None = None
    days_per_week: int | None = None
    periodization_type: str | None = None
    is_public: bool | None = None
    is_active: bool | None = None


class ProgramRead(ProgramBase):
    id: int
    user_id: int | None
    created_at: datetime
    updated_at: datetime | None

