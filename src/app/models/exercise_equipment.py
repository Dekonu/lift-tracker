from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class ExerciseEquipment(Base):
    """Many-to-many relationship between exercises and equipment."""

    __tablename__ = "exercise_equipment"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise.id"), nullable=False, index=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=False, index=True)
