from sqlalchemy import ForeignKey, String, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base

# Association table for many-to-many relationship between Exercise and MuscleGroup
exercise_secondary_muscle_groups = Table(
    "exercise_secondary_muscle_groups",
    Base.metadata,
    Column("exercise_id", Integer, ForeignKey("exercise.id", ondelete="CASCADE"), primary_key=True),
    Column("muscle_group_id", Integer, ForeignKey("muscle_group.id", ondelete="CASCADE"), primary_key=True),
)


class Exercise(Base):
    __tablename__ = "exercise"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    primary_muscle_group_id: Mapped[int] = mapped_column(ForeignKey("muscle_group.id"), index=True)

    # Relationships
    primary_muscle_group: Mapped["MuscleGroup"] = relationship(
        "MuscleGroup", foreign_keys=[primary_muscle_group_id], back_populates="primary_exercises", init=False
    )
    secondary_muscle_groups: Mapped[list["MuscleGroup"]] = relationship(
        "MuscleGroup",
        secondary=exercise_secondary_muscle_groups,
        back_populates="secondary_exercises",
        init=False,
    )
    exercise_instances: Mapped[list["ExerciseInstance"]] = relationship(
        "ExerciseInstance", back_populates="exercise", cascade="all, delete-orphan", init=False
    )

