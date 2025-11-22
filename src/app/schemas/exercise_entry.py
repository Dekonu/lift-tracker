from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .set_entry import SetEntryRead


class ExerciseEntryBase(BaseModel):
    exercise_id: Annotated[int, Field(gt=0)]
    notes: Annotated[str | None, Field(max_length=500, default=None)]
    order: Annotated[int, Field(ge=0, default=0)]


class ExerciseEntryCreate(ExerciseEntryBase):
    workout_session_id: int


class ExerciseEntryUpdate(BaseModel):
    notes: str | None = None
    order: int | None = None


class ExerciseEntryRead(ExerciseEntryBase):
    id: int
    workout_session_id: int
    created_at: datetime
    sets: list["SetEntryRead"] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)

