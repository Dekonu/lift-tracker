from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .set import SetRead


class ExerciseInstanceBase(BaseModel):
    exercise_id: Annotated[int, Field(gt=0, examples=[1])]
    order: Annotated[int, Field(ge=0, examples=[0])]


class ExerciseInstanceRead(ExerciseInstanceBase):
    id: int
    workout_id: int
    sets: list[SetRead] = []  # noqa: F821

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ExerciseInstanceCreate(ExerciseInstanceBase):
    model_config = ConfigDict(extra="forbid")


class ExerciseInstanceCreateInternal(ExerciseInstanceBase):
    workout_id: int


class ExerciseInstanceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    exercise_id: Annotated[int | None, Field(gt=0, examples=[1], default=None)]
    order: Annotated[int | None, Field(ge=0, examples=[0], default=None)]
