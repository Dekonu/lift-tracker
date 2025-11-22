from typing import Annotated

from pydantic import BaseModel, Field


class ExerciseCategoryBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50, examples=["Compound"])]
    description: Annotated[str | None, Field(max_length=200, default=None)]


class ExerciseCategoryCreate(ExerciseCategoryBase):
    pass


class ExerciseCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ExerciseCategoryRead(ExerciseCategoryBase):
    id: int

