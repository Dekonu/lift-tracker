from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base


class ExerciseEntry(Base):
    """Exercise entry within a workout session (contains sets)."""

    __tablename__ = "exercise_entry"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    workout_session_id: Mapped[int] = mapped_column(ForeignKey("workout_session.id"), nullable=False, index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise.id"), nullable=False, index=True)

    # Exercise-specific notes (fields with defaults)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # Order within workout

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))

    # Relationships
    sets: Mapped[list["SetEntry"]] = relationship(  # noqa: F821
        "SetEntry",
        back_populates="exercise_entry",
        cascade="all, delete-orphan",
        order_by="SetEntry.set_number",
        init=False,
    )
