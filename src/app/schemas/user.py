from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema
from ..models.user import Gender, NetWeightGoal, StrengthGoal


class UserBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]


class User(TimestampSchema, UserBase, UUIDSchema, PersistentDeletion):
    profile_image_url: Annotated[str, Field(default="https://www.profileimageurl.com")]
    hashed_password: str
    is_superuser: bool = False
    tier_id: int | None = None


class UserRead(BaseModel):
    id: int

    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]
    profile_image_url: str
    tier_id: int | None
    is_superuser: bool = False
    gender: Gender | None = None
    weight_lbs: float | None = None
    height_ft: int | None = None
    height_in: int | None = None
    birthdate: date | None = None
    net_weight_goal: NetWeightGoal | None = None
    strength_goals: list[StrengthGoal] | None = None


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")

    password: Annotated[str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Str1ngst!"])]


class UserCreateInternal(UserBase):
    hashed_password: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,  # Use enum values instead of enum names when serializing
    )

    name: Annotated[str | None, Field(min_length=2, max_length=30, examples=["User Userberg"], default=None)]
    email: Annotated[EmailStr | None, Field(examples=["user.userberg@example.com"], default=None)]
    profile_image_url: Annotated[
        str | None,
        Field(
            pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", examples=["https://www.profileimageurl.com"], default=None
        ),
    ]
    gender: Annotated[Gender | None, Field(default=None, examples=[Gender.MALE])]
    weight_lbs: Annotated[float | None, Field(gt=0, default=None, examples=[159.0])]
    height_ft: Annotated[int | None, Field(ge=0, le=8, default=None, examples=[5])]
    height_in: Annotated[int | None, Field(ge=0, lt=12, default=None, examples=[9])]
    birthdate: Annotated[date | None, Field(default=None, examples=["1994-03-26"])]
    net_weight_goal: Annotated[NetWeightGoal | None, Field(default=None, examples=[NetWeightGoal.MAINTAIN])]
    strength_goals: Annotated[list[StrengthGoal] | None, Field(default=None, examples=[[StrengthGoal.OVERALL_HEALTH, StrengthGoal.PERSONAL_MILESTONES]])]


class UserUpdateInternal(UserUpdate):
    updated_at: datetime


class UserTierUpdate(BaseModel):
    tier_id: int


class UserDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


class UserRestoreDeleted(BaseModel):
    is_deleted: bool
