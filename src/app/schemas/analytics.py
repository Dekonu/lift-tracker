from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class VolumeTrackingBase(BaseModel):
    muscle_group_id: int
    period_start: datetime
    period_end: datetime
    period_type: Annotated[str, Field(examples=["week", "month", "year"])]
    total_volume_kg: Annotated[float, Field(ge=0)]
    total_sets: Annotated[int, Field(ge=0)]
    total_reps: Annotated[int, Field(ge=0)]
    average_intensity: Annotated[float | None, Field(ge=0, le=100, default=None)]


class VolumeTrackingCreate(VolumeTrackingBase):
    user_id: int


class VolumeTrackingRead(VolumeTrackingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None


class StrengthProgressionBase(BaseModel):
    exercise_id: int
    date: datetime
    estimated_1rm_kg: Annotated[float, Field(gt=0)]
    volume_kg: Annotated[float, Field(ge=0)]
    average_rpe: Annotated[float | None, Field(ge=1.0, le=10.0, default=None)]


class StrengthProgressionCreate(StrengthProgressionBase):
    user_id: int


class StrengthProgressionRead(StrengthProgressionBase):
    id: int
    user_id: int
    created_at: datetime

