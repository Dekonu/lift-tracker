from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .template_set_entry import TemplateSetEntryCreate, TemplateSetEntryRead


class TemplateExerciseEntryBase(BaseModel):
    exercise_id: Annotated[int, Field(gt=0)]
    notes: Annotated[str | None, Field(max_length=500, default=None)]
    order: Annotated[int, Field(ge=0, default=0)]


class TemplateExerciseEntryCreate(TemplateExerciseEntryBase):
    workout_template_id: int | None = None  # Will be set when creating
    template_sets: list["TemplateSetEntryCreate"] = []  # noqa: F821


class TemplateExerciseEntryUpdate(BaseModel):
    exercise_id: int | None = None
    notes: str | None = None
    order: int | None = None


class TemplateExerciseEntryRead(TemplateExerciseEntryBase):
    id: int
    workout_template_id: int
    template_sets: list["TemplateSetEntryRead"] = []  # noqa: F821
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

