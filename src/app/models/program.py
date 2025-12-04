from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class Program(Base):
    """Multi-week training program."""

    __tablename__ = "program"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Program structure (fields without defaults first)
    duration_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    days_per_week: Mapped[int] = mapped_column(Integer, nullable=False)
    periodization_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'linear', 'undulating', 'block', etc.

    # Fields with defaults last
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id"), nullable=True, default=None, index=True
    )  # None = public program
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True, default=None)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
