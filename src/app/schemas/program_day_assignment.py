from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .workout_template import WorkoutTemplateRead


class ProgramDayAssignmentBase(BaseModel):
    week_number: Annotated[int, Field(gt=0, examples=[1])]
    day_number: Annotated[int, Field(ge=1, le=7, examples=[1])]  # Day 1-7 (not tied to calendar)
    workout_template_id: Annotated[int, Field(gt=0)]
    order: Annotated[int, Field(ge=0, default=0)]  # Order when multiple templates on same day


class ProgramDayAssignmentCreate(ProgramDayAssignmentBase):
    program_id: int


class ProgramDayAssignmentUpdate(BaseModel):
    week_number: int | None = None
    day_number: int | None = None
    workout_template_id: int | None = None
    order: int | None = None


class ProgramDayAssignmentRead(ProgramDayAssignmentBase):
    id: int
    program_id: int
    workout_template: "WorkoutTemplateRead | None" = None  # noqa: F821

    model_config = ConfigDict(from_attributes=True)

