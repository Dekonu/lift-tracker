from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class WorkoutSession(Base):
    """Actual logged workout session."""
    __tablename__ = "workout_session"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    
    # Session metadata (fields without defaults first)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Fields with defaults last
    workout_template_id: Mapped[int | None] = mapped_column(ForeignKey("workout_template.id"), nullable=True, default=None, index=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True, default=None)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    
    # Performance metrics (calculated)
    total_volume_kg: Mapped[float | None] = mapped_column(nullable=True, default=None)
    total_sets: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

