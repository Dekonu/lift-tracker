from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class OneRM(Base):
    """1RM (one-rep max) tracking for exercises."""

    __tablename__ = "one_rm"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise.id"), nullable=False, index=True)

    # 1RM data
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    is_estimated: Mapped[bool] = mapped_column(default=True, nullable=False)  # True if calculated, False if tested
    tested_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    # Calculation method (if estimated)
    calculation_method: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default=None
    )  # 'epley', 'brzycki', etc.
    based_on_weight: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    based_on_reps: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
