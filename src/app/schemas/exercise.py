from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ExerciseBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100, examples=["Bench Press"])]
    primary_muscle_group_id: Annotated[int, Field(gt=0, examples=[1])]
    secondary_muscle_group_ids: Annotated[list[int], Field(default_factory=list, examples=[[2, 3]])]


class ExerciseRead(ExerciseBase):
    id: int
    primary_muscle_group_id: int
    secondary_muscle_group_ids: list[int] = []


class ExerciseCreate(ExerciseBase):
    model_config = ConfigDict(extra="forbid")


class ExerciseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(min_length=1, max_length=100, examples=["Bench Press"], default=None)]
    primary_muscle_group_id: Annotated[int | None, Field(gt=0, examples=[1], default=None)]
    secondary_muscle_group_ids: Annotated[list[int] | None, Field(default=None, examples=[[2, 3]])]

