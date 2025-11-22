from datetime import UTC, datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class ShareableResourceType(str, PyEnum):
    """Types of resources that can be shared."""
    WORKOUT_TEMPLATE = "workout_template"
    PROGRAM = "program"
    WORKOUT_SESSION = "workout_session"


class SharingPermission(Base):
    """Sharing permissions for resources."""
    __tablename__ = "sharing_permission"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    resource_type: Mapped[ShareableResourceType] = mapped_column(Enum(ShareableResourceType), nullable=False)
    resource_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    shared_with_user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True, index=True)  # None = public
    
    # Permission level
    can_view: Mapped[bool] = mapped_column(default=True, nullable=False)
    can_edit: Mapped[bool] = mapped_column(default=False, nullable=False)
    can_copy: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

