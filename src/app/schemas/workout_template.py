from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class WorkoutTemplateBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100, examples=["Push Day"])]
    description: Annotated[str | None, Field(max_length=500, default=None)]
    is_public: Annotated[bool, Field(default=False)]
    estimated_duration_minutes: Annotated[int | None, Field(gt=0, default=None, examples=[60])]


class WorkoutTemplateCreate(WorkoutTemplateBase):
    user_id: int | None = None


class WorkoutTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_public: bool | None = None
    estimated_duration_minutes: int | None = None


class WorkoutTemplateRead(WorkoutTemplateBase):
    id: int
    user_id: int | None
    created_at: datetime
    updated_at: datetime | None

