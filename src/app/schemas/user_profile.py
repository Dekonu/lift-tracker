from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from ..models.user_profile import ExperienceLevel, Goal, TrainingStyle


class UserProfileBase(BaseModel):
    goal: Annotated[Goal, Field(examples=[Goal.GAIN_STRENGTH])]
    experience_level: Annotated[ExperienceLevel, Field(examples=[ExperienceLevel.INTERMEDIATE])]
    training_style: Annotated[TrainingStyle | None, Field(default=None, examples=[TrainingStyle.POWERLIFTING])]
    training_frequency_days_per_week: Annotated[int | None, Field(gt=0, le=7, default=None, examples=[4])]
    preferred_workout_duration_minutes: Annotated[int | None, Field(gt=0, default=None, examples=[60])]
    current_weight_kg: Annotated[float | None, Field(gt=0, default=None, examples=[75.5])]
    target_weight_kg: Annotated[float | None, Field(gt=0, default=None, examples=[80.0])]
    target_date: Annotated[datetime | None, Field(default=None)]
    notes: Annotated[str | None, Field(max_length=1000, default=None)]
    injury_limitations: Annotated[str | None, Field(max_length=500, default=None)]


class UserProfileCreate(UserProfileBase):
    user_id: int


class UserProfileUpdate(BaseModel):
    goal: Goal | None = None
    experience_level: ExperienceLevel | None = None
    training_style: TrainingStyle | None = None
    training_frequency_days_per_week: int | None = None
    preferred_workout_duration_minutes: int | None = None
    current_weight_kg: float | None = None
    target_weight_kg: float | None = None
    target_date: datetime | None = None
    notes: str | None = None
    injury_limitations: str | None = None


class UserProfileRead(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None

