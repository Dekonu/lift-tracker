from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base


class MuscleGroup(Base):
    __tablename__ = "muscle_group"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

