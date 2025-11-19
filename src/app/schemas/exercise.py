from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..core.utils.string_utils import to_camel_case, validate_exercise_name


class ExerciseBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100, examples=["benchPress"])]
    primary_muscle_group_id: Annotated[int, Field(gt=0, examples=[1])]
    secondary_muscle_group_ids: Annotated[list[int], Field(default_factory=list, examples=[[2, 3]])]
    
    @field_validator('name', mode='before')
    @classmethod
    def validate_and_convert_name(cls, v: str) -> str:
        """Validate and convert exercise name to camelCase."""
        if isinstance(v, str):
            return validate_exercise_name(v)
        return v


class ExerciseRead(ExerciseBase):
    id: int
    primary_muscle_group_id: int
    secondary_muscle_group_ids: list[int] = []


class ExerciseCreate(ExerciseBase):
    model_config = ConfigDict(extra="forbid")


class ExerciseCreateInternal(ExerciseBase):
    """Internal schema for creating exercises."""
    model_config = ConfigDict(extra="forbid")


class ExerciseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(min_length=1, max_length=100, examples=["benchPress"], default=None)]
    primary_muscle_group_id: Annotated[int | None, Field(gt=0, examples=[1], default=None)]
    secondary_muscle_group_ids: Annotated[list[int] | None, Field(default=None, examples=[[2, 3]])]
    
    @field_validator('name', mode='before')
    @classmethod
    def validate_and_convert_name(cls, v: str | None) -> str | None:
        """Validate and convert exercise name to camelCase."""
        if v is None:
            return None
        if isinstance(v, str):
            return validate_exercise_name(v)
        return v

