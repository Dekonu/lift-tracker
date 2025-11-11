from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base


class ExerciseInstance(Base):
    __tablename__ = "exercise_instance"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    workout_id: Mapped[int] = mapped_column(ForeignKey("workout.id", ondelete="CASCADE"), index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise.id", ondelete="CASCADE"), index=True)
    order: Mapped[int] = mapped_column(Integer, index=True)

    # Relationships
    workout: Mapped["Workout"] = relationship("Workout", back_populates="exercise_instances", init=False)
    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="exercise_instances", init=False)
    sets: Mapped[list["Set"]] = relationship(
        "Set", back_populates="exercise_instance", cascade="all, delete-orphan", order_by="Set.id", init=False
    )

