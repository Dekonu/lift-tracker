from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .program import ProgramRead
    from .workout_session import WorkoutSessionRead
    from .workout_template import WorkoutTemplateRead


class ScheduledWorkoutBase(BaseModel):
    scheduled_date: Annotated[datetime, Field(examples=["2024-01-01T10:00:00Z"])]
    workout_template_id: Annotated[int, Field(examples=[1])]
    program_id: Annotated[int | None, Field(default=None, examples=[1])]
    program_week: Annotated[int | None, Field(default=None, examples=[1])]
    status: Annotated[str, Field(default="scheduled", examples=["scheduled"])]
    notes: Annotated[str | None, Field(default=None, max_length=500)]


class ScheduledWorkoutCreate(ScheduledWorkoutBase):
    user_id: int | None = None  # Will be set from current_user if not provided


class ScheduledWorkoutUpdate(BaseModel):
    scheduled_date: datetime | None = None
    workout_template_id: int | None = None
    status: str | None = None
    notes: str | None = None
    completed_workout_session_id: int | None = None


class ScheduledWorkoutRead(ScheduledWorkoutBase):
    id: int
    user_id: int
    completed_workout_session_id: int | None
    created_at: datetime
    updated_at: datetime | None
    workout_template: Annotated[WorkoutTemplateRead | None, Field(default=None)]
    program: Annotated[ProgramRead | None, Field(default=None)]
    completed_session: Annotated[WorkoutSessionRead | None, Field(default=None)]

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
