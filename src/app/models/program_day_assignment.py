from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base


class ProgramDayAssignment(Base):
    """Assignment of workout templates to specific days (1-7) within a program week.
    
    This allows multiple templates per day and supports flexible scheduling
    where users can start their week on any day.
    """

    __tablename__ = "program_day_assignment"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    program_id: Mapped[int] = mapped_column(ForeignKey("program.id"), nullable=False, index=True)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)  # Week within the program (1-based)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)  # Day of week (1-7, not tied to calendar)
    workout_template_id: Mapped[int] = mapped_column(
        ForeignKey("workout_template.id"), nullable=False, index=True
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # Order when multiple templates on same day

    # Relationships
    program: Mapped["Program"] = relationship("Program", init=False)  # noqa: F821
    workout_template: Mapped["WorkoutTemplate"] = relationship("WorkoutTemplate", init=False)  # noqa: F821

    __table_args__ = (
        UniqueConstraint("program_id", "week_number", "day_number", "workout_template_id", "order", name="uq_program_day_assignment"),
    )

