from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class ExerciseVariation(Base):
    """Exercise variations - easier/harder progressions of exercises."""

    __tablename__ = "exercise_variation"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise.id"), nullable=False, index=True)
    variation_exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise.id"), nullable=False, index=True)
    variation_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'easier', 'harder', 'alternative'

    # Fields with defaults
    notes: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)
