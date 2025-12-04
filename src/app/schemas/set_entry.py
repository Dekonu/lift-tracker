from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class SetEntryBase(BaseModel):
    set_number: Annotated[int, Field(gt=0)]
    weight_kg: Annotated[float | None, Field(gt=0, default=None)]
    reps: Annotated[int | None, Field(gt=0, default=None)]
    rir: Annotated[int | None, Field(ge=0, le=5, default=None, examples=[2])]  # Reps in Reserve
    rpe: Annotated[float | None, Field(ge=1.0, le=10.0, default=None, examples=[8.0])]  # Rate of Perceived Exertion
    percentage_of_1rm: Annotated[float | None, Field(gt=0, le=100, default=None, examples=[85.0])]
    rest_seconds: Annotated[int | None, Field(gt=0, default=None, examples=[180])]
    tempo: Annotated[str | None, Field(max_length=20, default=None, examples=["3-1-1-0"])]
    notes: Annotated[str | None, Field(max_length=200, default=None)]
    is_warmup: Annotated[bool, Field(default=False)]


class SetEntryCreate(SetEntryBase):
    exercise_entry_id: int


class SetEntryUpdate(BaseModel):
    set_number: int | None = None
    weight_kg: float | None = None
    reps: int | None = None
    rir: int | None = None
    rpe: float | None = None
    percentage_of_1rm: float | None = None
    rest_seconds: int | None = None
    tempo: str | None = None
    notes: str | None = None
    is_warmup: bool | None = None


class SetEntryRead(SetEntryBase):
    id: int
    exercise_entry_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
