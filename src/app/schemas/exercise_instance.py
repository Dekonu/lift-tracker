from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ExerciseInstanceBase(BaseModel):
    exercise_id: Annotated[int, Field(gt=0, examples=[1])]
    order: Annotated[int, Field(ge=0, examples=[0])]


class ExerciseInstanceRead(ExerciseInstanceBase):
    id: int
    workout_id: int
    sets: list["SetRead"] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ExerciseInstanceCreate(ExerciseInstanceBase):
    model_config = ConfigDict(extra="forbid")


class ExerciseInstanceCreateInternal(ExerciseInstanceBase):
    workout_id: int


class ExerciseInstanceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    exercise_id: Annotated[int | None, Field(gt=0, examples=[1], default=None)]
    order: Annotated[int | None, Field(ge=0, examples=[0], default=None)]

