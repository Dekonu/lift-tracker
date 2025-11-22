from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class VolumeTracking(Base):
    """Volume tracking per muscle group per time period."""
    __tablename__ = "volume_tracking"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    muscle_group_id: Mapped[int] = mapped_column(ForeignKey("muscle_group.id"), nullable=False, index=True)
    
    # Time period
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'week', 'month', 'year'
    
    # Volume metrics
    total_volume_kg: Mapped[float] = mapped_column(Float, nullable=False)
    total_sets: Mapped[int] = mapped_column(Integer, nullable=False)
    total_reps: Mapped[int] = mapped_column(Integer, nullable=False)
    average_intensity: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)  # % of 1RM
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)


class StrengthProgression(Base):
    """Strength progression tracking for exercises."""
    __tablename__ = "strength_progression"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise.id"), nullable=False, index=True)
    
    # Progression data
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    estimated_1rm_kg: Mapped[float] = mapped_column(Float, nullable=False)
    volume_kg: Mapped[float] = mapped_column(Float, nullable=False)
    average_rpe: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))

