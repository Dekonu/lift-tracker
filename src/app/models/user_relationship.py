from datetime import UTC, datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class RelationshipType(str, PyEnum):
    """Types of user relationships."""

    FOLLOW = "follow"  # One-way follow
    FRIEND = "friend"  # Mutual friendship
    BLOCK = "block"  # Blocked user


class UserRelationship(Base):
    """User relationships for social features."""

    __tablename__ = "user_relationship"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    related_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    relationship_type: Mapped[RelationshipType] = mapped_column(Enum(RelationshipType), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
