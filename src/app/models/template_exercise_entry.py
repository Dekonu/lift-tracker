from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base


class TemplateExerciseEntry(Base):
    """Exercise entry within a workout template (contains template sets)."""

    __tablename__ = "template_exercise_entry"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    workout_template_id: Mapped[int] = mapped_column(
        ForeignKey("workout_template.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise.id"), nullable=False, index=True)

    # Exercise-specific notes (fields with defaults)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # Order within workout

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))

    # Relationships
    workout_template: Mapped["WorkoutTemplate"] = relationship(
        "WorkoutTemplate", back_populates="template_exercises", init=False
    )  # noqa: F821
    template_sets: Mapped[list["TemplateSetEntry"]] = relationship(  # noqa: F821
        "TemplateSetEntry",
        back_populates="template_exercise_entry",
        cascade="all, delete-orphan",
        order_by="TemplateSetEntry.set_number",
        init=False,
    )

