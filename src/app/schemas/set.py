from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..models.set import WeightType, WeightUnit


class SetBase(BaseModel):
    weight_value: Annotated[float, Field(gt=0, examples=[135.5])]
    weight_type: Annotated[WeightType, Field(examples=[WeightType.STATIC])]
    unit: Annotated[WeightUnit, Field(examples=[WeightUnit.POUNDS])]
    rest_time_seconds: Annotated[int | None, Field(gt=0, examples=[90], default=None)]
    rir: Annotated[int | None, Field(ge=0, examples=[2], default=None)]  # Reps in Reserve
    notes: Annotated[str | None, Field(max_length=1000, examples=["Felt strong today"], default=None)]


class SetRead(SetBase):
    id: int
    exercise_instance_id: int


class SetCreate(SetBase):
    model_config = ConfigDict(extra="forbid")


class SetCreateInternal(SetBase):
    exercise_instance_id: int


class SetUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weight_value: Annotated[float | None, Field(gt=0, examples=[135.5], default=None)]
    weight_type: Annotated[WeightType | None, Field(examples=[WeightType.STATIC], default=None)]
    unit: Annotated[WeightUnit | None, Field(examples=[WeightUnit.POUNDS], default=None)]
    rest_time_seconds: Annotated[int | None, Field(gt=0, examples=[90], default=None)]
    rir: Annotated[int | None, Field(ge=0, examples=[2], default=None)]
    notes: Annotated[str | None, Field(max_length=1000, examples=["Felt strong today"], default=None)]

