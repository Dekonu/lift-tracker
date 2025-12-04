from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base


class TemplateSetEntry(Base):
    """Individual set within a template exercise entry."""

    __tablename__ = "template_set_entry"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    template_exercise_entry_id: Mapped[int] = mapped_column(
        ForeignKey("template_exercise_entry.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Set data
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3, etc.
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    reps: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)

    # Advanced metrics
    rir: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)  # Reps in Reserve (0-5)
    rpe: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)  # Rate of Perceived Exertion (1-10)
    percentage_of_1rm: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)  # % of 1RM
    rest_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)  # Rest after this set

    # Tempo (e.g., "3-1-1-0" = 3s eccentric, 1s pause, 1s concentric, 0s hold)
    tempo: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)

    # Set notes
    notes: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)

    # Warmup/working set indicator
    is_warmup: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))

    # Relationships
    template_exercise_entry: Mapped["TemplateExerciseEntry"] = relationship(
        "TemplateExerciseEntry", back_populates="template_sets", init=False
    )  # noqa: F821

