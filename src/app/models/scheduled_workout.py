from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base


class ScheduledWorkout(Base):
    """Planned workout assigned to a specific date."""
    __tablename__ = "scheduled_workout"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    workout_template_id: Mapped[int] = mapped_column(ForeignKey("workout_template.id"), nullable=False, index=True)
    scheduled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    # Non-default fields first
    completed_workout_session_id: Mapped[int | None] = mapped_column(ForeignKey("workout_session.id"), nullable=True, index=True)
    
    # Fields with defaults last
    program_id: Mapped[int | None] = mapped_column(ForeignKey("program.id"), nullable=True, default=None, index=True)
    program_week: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(20), default="scheduled", nullable=False)  # scheduled, completed, skipped, in_progress
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    
    # Relationships
    workout_template: Mapped["WorkoutTemplate"] = relationship("WorkoutTemplate", init=False)
    program: Mapped["Program"] = relationship("Program", init=False)
    completed_session: Mapped["WorkoutSession"] = relationship("WorkoutSession", foreign_keys=[completed_workout_session_id], init=False)

