from typing import Annotated

from pydantic import BaseModel, Field


class ProgramWeekBase(BaseModel):
    program_id: int
    week_number: Annotated[int, Field(gt=0)]
    volume_modifier: Annotated[float | None, Field(gt=0, le=2.0, default=None, examples=[0.9, 1.0, 1.1])]
    intensity_modifier: Annotated[float | None, Field(gt=0, le=2.0, default=None, examples=[0.9, 1.0, 1.1])]
    notes: Annotated[str | None, Field(max_length=500, default=None)]
    workout_template_id: Annotated[int | None, Field(default=None)]


class ProgramWeekCreate(ProgramWeekBase):
    pass


class ProgramWeekUpdate(BaseModel):
    week_number: int | None = None
    volume_modifier: float | None = None
    intensity_modifier: float | None = None
    notes: str | None = None
    workout_template_id: int | None = None


class ProgramWeekUpdate(BaseModel):
    week_number: int | None = None
    volume_modifier: float | None = None
    intensity_modifier: float | None = None
    notes: str | None = None
    workout_template_id: int | None = None


class ProgramWeekRead(ProgramWeekBase):
    id: int
