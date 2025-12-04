from sqlalchemy import ARRAY, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base


class Exercise(Base):
    __tablename__ = "exercise"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    primary_muscle_group_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default_factory=list, init=False)
    secondary_muscle_group_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default_factory=list, init=False)

    # Exercise metadata (fields without defaults first)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("exercise_category.id"), nullable=True, default=None, index=True
    )
    instructions: Mapped[str | None] = mapped_column(String(2000), nullable=True, default=None)
    common_mistakes: Mapped[str | None] = mapped_column(String(1000), nullable=True, default=None)

    # Fields with defaults last
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    exercise_instances: Mapped[list["ExerciseInstance"]] = relationship(  # noqa: F821
        "ExerciseInstance", back_populates="exercise", cascade="all, delete-orphan", init=False
    )
