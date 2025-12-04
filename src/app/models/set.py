from enum import Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base


class WeightType(str, Enum):
    PERCENTAGE = "percentage"  # Percentage of 1RM
    STATIC = "static"  # Static weight value


class WeightUnit(str, Enum):
    POUNDS = "lbs"
    KILOGRAMS = "kg"


class Set(Base):
    __tablename__ = "set"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    exercise_instance_id: Mapped[int] = mapped_column(
        ForeignKey("exercise_instance.id", ondelete="CASCADE"), index=True
    )
    weight_value: Mapped[float] = mapped_column(Float)
    weight_type: Mapped[WeightType] = mapped_column(SQLEnum(WeightType), index=True)
    unit: Mapped[WeightUnit] = mapped_column(SQLEnum(WeightUnit), index=True)
    rest_time_seconds: Mapped[int | None] = mapped_column(Integer, default=None)
    rir: Mapped[int | None] = mapped_column(Integer, default=None)  # Reps in Reserve
    notes: Mapped[str | None] = mapped_column(Text, default=None)

    # Relationships
    exercise_instance: Mapped["ExerciseInstance"] = relationship("ExerciseInstance", back_populates="sets", init=False)  # noqa: F821
