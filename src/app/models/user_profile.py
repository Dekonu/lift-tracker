from datetime import UTC, datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class Goal(str, PyEnum):
    """User fitness goals."""
    GAIN_STRENGTH = "gain_strength"
    GAIN_MUSCLE = "gain_muscle"
    LOSE_WEIGHT = "lose_weight"
    MAINTAIN = "maintain"
    IMPROVE_ENDURANCE = "improve_endurance"
    SPORT_SPECIFIC = "sport_specific"


class ExperienceLevel(str, PyEnum):
    """User experience levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TrainingStyle(str, PyEnum):
    """Preferred training styles."""
    POWERLIFTING = "powerlifting"
    BODYBUILDING = "bodybuilding"
    GENERAL_FITNESS = "general_fitness"
    CALISTHENICS = "calisthenics"
    CROSSFIT = "crossfit"


class UserProfile(Base):
    """User profile with fitness goals, experience, and preferences."""
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True, index=True, nullable=False)
    
    # Goals and experience
    goal: Mapped[Goal] = mapped_column(Enum(Goal), nullable=False)
    experience_level: Mapped[ExperienceLevel] = mapped_column(Enum(ExperienceLevel), nullable=False)
    training_style: Mapped[TrainingStyle | None] = mapped_column(Enum(TrainingStyle), nullable=True, default=None)
    
    # Training preferences
    training_frequency_days_per_week: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    preferred_workout_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    
    # Weight goals (for gain/lose weight)
    current_weight_kg: Mapped[float | None] = mapped_column(nullable=True, default=None)
    target_weight_kg: Mapped[float | None] = mapped_column(nullable=True, default=None)
    target_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    
    # Additional context
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True, default=None)
    injury_limitations: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

