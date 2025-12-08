from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...core.security import blacklist_token, get_password_hash, oauth2_scheme
from ...crud.crud_rate_limit import crud_rate_limits
from ...crud.crud_tier import crud_tiers
from ...crud.crud_users import crud_users
from ...schemas.tier import TierRead
from ...schemas.user import UserCreate, UserCreateInternal, UserRead, UserTierUpdate, UserUpdate

router = APIRouter(tags=["users"])


@router.post("/user", response_model=UserRead, status_code=201)
async def write_user(
    request: Request, user: UserCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> UserRead:
    email_row = await crud_users.exists(db=db, email=user.email)
    if email_row:
        raise DuplicateValueException("Email is already registered")

    user_internal_dict = user.model_dump()
    user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
    del user_internal_dict["password"]

    user_internal = UserCreateInternal(**user_internal_dict)
    created_user = await crud_users.create(db=db, object=user_internal)

    user_read = await crud_users.get(db=db, id=created_user.id, schema_to_select=UserRead)
    if user_read is None:
        raise NotFoundException("Created user not found")

    return cast(UserRead, user_read)


@router.get("/users", response_model=PaginatedListResponse[UserRead])
async def read_users(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    users_data = await crud_users.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/user/me/", response_model=UserRead)
async def read_users_me(request: Request, current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    return current_user


@router.get("/user/{user_id}", response_model=UserRead)
async def read_user(request: Request, user_id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> UserRead:
    db_user = await crud_users.get(db=db, id=user_id, is_deleted=False, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    return cast(UserRead, db_user)


@router.patch("/user/me")
async def patch_user(
    request: Request,
    values: UserUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    db_user = await crud_users.get(db=db, email=current_user["email"])
    if db_user is None:
        raise NotFoundException("User not found")

    if isinstance(db_user, dict):
        db_email = db_user["email"]
    else:
        db_email = db_user.email

    if values.email is not None and values.email != db_email:
        if await crud_users.exists(db=db, email=values.email):
            raise DuplicateValueException("Email is already registered")

    # Get the update data, keeping dates as date objects (not strings)
    # Use mode='python' to get Python objects (not JSON strings) but still convert enums
    update_data = values.model_dump(exclude_unset=True, mode='python')
    
    # Convert enum values to lowercase strings for database compatibility
    # Handle both enum instances and string values (which may be uppercase)
    from ...models.user import Gender, NetWeightGoal, StrengthGoal
    
    # Mapping from uppercase enum names to lowercase values
    GENDER_MAP = {name: enum.value for name, enum in Gender.__members__.items()}
    NET_WEIGHT_GOAL_MAP = {name: enum.value for name, enum in NetWeightGoal.__members__.items()}
    STRENGTH_GOAL_MAP = {name: enum.value for name, enum in StrengthGoal.__members__.items()}
    
    # Helper function to normalize enum values to lowercase strings
    def normalize_enum_value(value: Any, enum_class: type, enum_map: dict[str, str]) -> str | None:
        """Convert enum value to lowercase string."""
        if value is None:
            return None
        # Check if it's an enum instance first
        if isinstance(value, enum_class):
            return value.value
        # If it's a string, try to normalize it
        if isinstance(value, str):
            # Try to find in map first (handles uppercase enum names like 'MALE')
            normalized = enum_map.get(value.upper())
            if normalized:
                return normalized
            # If it's already lowercase and valid, return it
            if value.lower() in enum_map.values():
                return value.lower()
            # Fall back to lowercase
            return value.lower()
        # For any other type, convert to string and lowercase
        return str(value).lower()
    
    # Normalize gender - always convert if present
    if "gender" in update_data:
        original_gender = update_data["gender"]
        update_data["gender"] = normalize_enum_value(original_gender, Gender, GENDER_MAP)
    
    # Normalize net_weight_goal - always convert if present
    if "net_weight_goal" in update_data:
        original_goal = update_data["net_weight_goal"]
        update_data["net_weight_goal"] = normalize_enum_value(original_goal, NetWeightGoal, NET_WEIGHT_GOAL_MAP)
    
    # Normalize strength_goals array - always convert if present
    if "strength_goals" in update_data and update_data["strength_goals"] is not None:
        normalized_goals = [
            normalize_enum_value(goal, StrengthGoal, STRENGTH_GOAL_MAP)
            for goal in update_data["strength_goals"]
        ]
        update_data["strength_goals"] = normalized_goals
    
    # Ensure all enum values are lowercase strings before database update
    # Double-check in case something was missed
    if "gender" in update_data and update_data["gender"] is not None:
        if isinstance(update_data["gender"], str) and update_data["gender"].isupper():
            update_data["gender"] = GENDER_MAP.get(update_data["gender"], update_data["gender"].lower())
    if "net_weight_goal" in update_data and update_data["net_weight_goal"] is not None:
        if isinstance(update_data["net_weight_goal"], str) and update_data["net_weight_goal"].isupper():
            update_data["net_weight_goal"] = NET_WEIGHT_GOAL_MAP.get(update_data["net_weight_goal"], update_data["net_weight_goal"].lower())
    
    await crud_users.update(db=db, object=update_data, email=current_user["email"])
    return {"message": "User updated"}


@router.delete("/user/me")
async def erase_user(
    request: Request,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    db_user = await crud_users.get(db=db, email=current_user["email"], schema_to_select=UserRead)
    if not db_user:
        raise NotFoundException("User not found")

    await crud_users.delete(db=db, email=current_user["email"])
    await blacklist_token(token=token, db=db)
    return {"message": "User deleted"}


@router.delete("/db_user/{user_id}", dependencies=[Depends(get_current_superuser)])
async def erase_db_user(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    db_user = await crud_users.exists(db=db, id=user_id)
    if not db_user:
        raise NotFoundException("User not found")

    await crud_users.db_delete(db=db, id=user_id)
    await blacklist_token(token=token, db=db)
    return {"message": "User deleted from the database"}


@router.get("/user/{user_id}/rate_limits", dependencies=[Depends(get_current_superuser)])
async def read_user_rate_limits(
    request: Request, user_id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    db_user = await crud_users.get(db=db, id=user_id, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    db_user = cast(UserRead, db_user)
    user_dict = db_user.model_dump()
    if db_user.tier_id is None:
        user_dict["tier_rate_limits"] = []
        return user_dict

    db_tier = await crud_tiers.get(db=db, id=db_user.tier_id, schema_to_select=TierRead)
    if db_tier is None:
        raise NotFoundException("Tier not found")

    db_tier = cast(TierRead, db_tier)
    db_rate_limits = await crud_rate_limits.get_multi(db=db, tier_id=db_tier.id)

    user_dict["tier_rate_limits"] = db_rate_limits["data"]

    return user_dict


@router.get("/user/{user_id}/tier")
async def read_user_tier(
    request: Request, user_id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict | None:
    db_user = await crud_users.get(db=db, id=user_id, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    db_user = cast(UserRead, db_user)
    if db_user.tier_id is None:
        return None

    db_tier = await crud_tiers.get(db=db, id=db_user.tier_id, schema_to_select=TierRead)
    if not db_tier:
        raise NotFoundException("Tier not found")

    db_tier = cast(TierRead, db_tier)

    user_dict = db_user.model_dump()
    tier_dict = db_tier.model_dump()

    for key, value in tier_dict.items():
        user_dict[f"tier_{key}"] = value

    return user_dict


@router.patch("/user/{user_id}/tier", dependencies=[Depends(get_current_superuser)])
async def patch_user_tier(
    request: Request, user_id: int, values: UserTierUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_user = await crud_users.get(db=db, id=user_id, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    db_user = cast(UserRead, db_user)
    db_tier = await crud_tiers.get(db=db, id=values.tier_id, schema_to_select=TierRead)
    if db_tier is None:
        raise NotFoundException("Tier not found")

    await crud_users.update(db=db, object=values.model_dump(), id=user_id)
    return {"message": f"User {db_user.name} Tier updated"}
