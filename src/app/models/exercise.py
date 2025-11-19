from sqlalchemy import ARRAY, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base


class Exercise(Base):
    __tablename__ = "exercise"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    primary_muscle_group_id: Mapped[int] = mapped_column(ForeignKey("muscle_group.id"), index=True)
    secondary_muscle_group_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default_factory=list, init=False)

    # Relationships
    primary_muscle_group: Mapped["MuscleGroup"] = relationship(
        "MuscleGroup", foreign_keys=[primary_muscle_group_id], back_populates="primary_exercises", init=False
    )
    exercise_instances: Mapped[list["ExerciseInstance"]] = relationship(
        "ExerciseInstance", back_populates="exercise", cascade="all, delete-orphan", init=False
    )

