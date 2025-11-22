from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class OneRMBase(BaseModel):
    exercise_id: Annotated[int, Field(gt=0)]
    weight_kg: Annotated[float, Field(gt=0)]
    is_estimated: Annotated[bool, Field(default=True)]
    tested_date: Annotated[datetime | None, Field(default=None)]
    calculation_method: Annotated[str | None, Field(max_length=50, default=None, examples=["epley", "brzycki"])]
    based_on_weight: Annotated[float | None, Field(gt=0, default=None)]
    based_on_reps: Annotated[int | None, Field(gt=0, default=None)]


class OneRMCreate(OneRMBase):
    user_id: int


class OneRMUpdate(BaseModel):
    weight_kg: float | None = None
    is_estimated: bool | None = None
    tested_date: datetime | None = None
    calculation_method: str | None = None
    based_on_weight: float | None = None
    based_on_reps: int | None = None


class OneRMRead(OneRMBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None

