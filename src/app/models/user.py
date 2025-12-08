import uuid as uuid_pkg
from datetime import UTC, date, datetime
from enum import Enum as PyEnum

from sqlalchemy import ARRAY, Date, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from ..core.db.database import Base


class Gender(str, PyEnum):
    """User gender options."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class NetWeightGoal(str, PyEnum):
    """User net weight goal options."""

    GAIN = "gain"
    LOSE = "lose"
    MAINTAIN = "maintain"


class StrengthGoal(str, PyEnum):
    """User strength training goal options."""

    OVERALL_HEALTH = "overall_health"
    COMPETE = "compete"
    PERSONAL_MILESTONES = "personal_milestones"
    BODYBUILDING = "bodybuilding"
    POWERLIFTING = "powerlifting"
    FUNCTIONAL_STRENGTH = "functional_strength"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    profile_image_url: Mapped[str] = mapped_column(String, default="https://profileimageurl.com")
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), default_factory=uuid7, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    tier_id: Mapped[int | None] = mapped_column(ForeignKey("tier.id"), index=True, default=None, init=False)

    # Optional personal information fields
    gender: Mapped[Gender | None] = mapped_column(
        Enum(Gender, native_enum=False, create_constraint=False, length=20), nullable=True, default=None
    )
    weight_lbs: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    height_ft: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    height_in: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    birthdate: Mapped[date | None] = mapped_column(Date, nullable=True, default=None)
    net_weight_goal: Mapped[NetWeightGoal | None] = mapped_column(
        Enum(NetWeightGoal, native_enum=False, create_constraint=False, length=20), nullable=True, default=None
    )
    strength_goals: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(30)), nullable=True, default=None
    )
