from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .template_exercise_entry import TemplateExerciseEntryRead


class WorkoutTemplateBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100, examples=["Push Day"])]
    description: Annotated[str | None, Field(max_length=500, default=None)]
    is_public: Annotated[bool, Field(default=False)]
    estimated_duration_minutes: Annotated[int | None, Field(gt=0, default=None, examples=[60])]


class WorkoutTemplateCreate(WorkoutTemplateBase):
    user_id: int | None = None
    template_exercises: list["TemplateExerciseEntryCreate"] = []  # noqa: F821


class WorkoutTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_public: bool | None = None
    estimated_duration_minutes: int | None = None


class WorkoutTemplateRead(WorkoutTemplateBase):
    id: int
    user_id: int | None
    template_exercises: list["TemplateExerciseEntryRead"] = []  # noqa: F821
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
