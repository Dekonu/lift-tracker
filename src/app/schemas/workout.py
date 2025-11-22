from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .exercise_instance import ExerciseInstanceRead


class WorkoutBase(BaseModel):
    date: Annotated[datetime, Field(examples=["2024-01-15T10:00:00Z"])]


class WorkoutRead(WorkoutBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None
    exercise_instances: list["ExerciseInstanceRead"] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)


class WorkoutCreate(WorkoutBase):
    model_config = ConfigDict(extra="forbid")


class WorkoutCreateInternal(WorkoutBase):
    user_id: int


class WorkoutUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: Annotated[datetime | None, Field(examples=["2024-01-15T10:00:00Z"], default=None)]

