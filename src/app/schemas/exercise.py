from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..core.utils.string_utils import to_camel_case, validate_exercise_name, validate_exercise_name_preserve_format


class ExerciseBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100, examples=["benchPress"])]
    primary_muscle_group_ids: Annotated[list[int], Field(min_length=1, examples=[[1], [1, 2]])]
    secondary_muscle_group_ids: Annotated[list[int], Field(default_factory=list, examples=[[2, 3]])]
    equipment_ids: Annotated[list[int], Field(default_factory=list, examples=[[1, 2]])]  # Required equipment
    enabled: Annotated[bool, Field(default=True, examples=[True])]
    
    @field_validator('name', mode='before')
    @classmethod
    def validate_and_convert_name(cls, v: str) -> str:
        """Validate exercise name while preserving original formatting."""
        if isinstance(v, str):
            return validate_exercise_name_preserve_format(v)
        return v


class ExerciseRead(ExerciseBase):
    id: int
    primary_muscle_group_ids: list[int]
    secondary_muscle_group_ids: list[int] = []
    equipment_ids: list[int] = []
    enabled: bool = True


class ExerciseCreate(ExerciseBase):
    model_config = ConfigDict(extra="forbid")


class ExerciseCreateInternal(BaseModel):
    """Internal schema for creating exercises without muscle group arrays (they have init=False)."""
    name: Annotated[str, Field(min_length=1, max_length=100, examples=["benchPress"])]
    enabled: Annotated[bool, Field(default=True, examples=[True])]
    
    @field_validator('name', mode='before')
    @classmethod
    def validate_and_convert_name(cls, v: str) -> str:
        """Validate exercise name while preserving original formatting."""
        if isinstance(v, str):
            return validate_exercise_name_preserve_format(v)
        return v
    
    model_config = ConfigDict(extra="forbid")


class ExerciseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(min_length=1, max_length=100, examples=["benchPress"], default=None)]
    primary_muscle_group_ids: Annotated[list[int] | None, Field(min_length=1, examples=[[1], [1, 2]], default=None)]
    secondary_muscle_group_ids: Annotated[list[int] | None, Field(default=None, examples=[[2, 3]])]
    equipment_ids: Annotated[list[int] | None, Field(default=None, examples=[[1, 2]])]
    enabled: Annotated[bool | None, Field(default=None, examples=[True, False])]
    
    @field_validator('name', mode='before')
    @classmethod
    def validate_and_convert_name(cls, v: str | None) -> str | None:
        """Validate exercise name while preserving original formatting."""
        if v is None:
            return None
        if isinstance(v, str):
            return validate_exercise_name_preserve_format(v)
        return v

