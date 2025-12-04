from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base


class Workout(Base):
    __tablename__ = "workout"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    # Relationships
    user: Mapped["User"] = relationship("User", init=False)  # noqa: F821
    exercise_instances: Mapped[list["ExerciseInstance"]] = relationship(  # noqa: F821
        "ExerciseInstance",
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="ExerciseInstance.order",
        init=False,
    )
