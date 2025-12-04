from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class ProgramWeek(Base):
    """Week within a program (for periodization)."""

    __tablename__ = "program_week"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    program_id: Mapped[int] = mapped_column(ForeignKey("program.id"), nullable=False, index=True)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Periodization parameters (fields with defaults)
    volume_modifier: Mapped[float | None] = mapped_column(nullable=True, default=None)  # e.g., 0.9 for deload
    intensity_modifier: Mapped[float | None] = mapped_column(nullable=True, default=None)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    workout_template_id: Mapped[int | None] = mapped_column(
        ForeignKey("workout_template.id"), nullable=True, default=None, index=True
    )
