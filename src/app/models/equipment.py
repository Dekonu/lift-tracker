from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class Equipment(Base):
    """Equipment available for exercises."""
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

