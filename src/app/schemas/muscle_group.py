from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class MuscleGroupBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50, examples=["Chest"])]


class MuscleGroupRead(MuscleGroupBase):
    id: int


class MuscleGroupCreate(MuscleGroupBase):
    model_config = ConfigDict(extra="forbid")


class MuscleGroupUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(min_length=1, max_length=50, examples=["Chest"], default=None)]

