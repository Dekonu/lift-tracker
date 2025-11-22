from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .exercise_entry import ExerciseEntryRead


class WorkoutSessionBase(BaseModel):
    name: Annotated[str | None, Field(max_length=100, default=None, examples=["Push Day"])]
    notes: Annotated[str | None, Field(max_length=1000, default=None)]
    started_at: Annotated[datetime, Field(examples=["2024-01-01T10:00:00Z"])]
    completed_at: Annotated[datetime | None, Field(default=None)]
    duration_minutes: Annotated[int | None, Field(gt=0, default=None)]
    workout_template_id: Annotated[int | None, Field(default=None)]


class WorkoutSessionCreate(WorkoutSessionBase):
    user_id: int | None = None  # Optional - will be set from current_user if not provided


class WorkoutSessionUpdate(BaseModel):
    name: str | None = None
    notes: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_minutes: int | None = None


class WorkoutSessionRead(WorkoutSessionBase):
    id: int
    user_id: int
    workout_template_id: int | None
    total_volume_kg: float | None
    total_sets: int | None
    created_at: datetime
    updated_at: datetime | None
    exercise_entries: list["ExerciseEntryRead"] = []

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

