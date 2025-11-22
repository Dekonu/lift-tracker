from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_user_profile import crud_user_profile
from ...schemas.user_profile import UserProfileCreate, UserProfileRead, UserProfileUpdate

router = APIRouter(tags=["user-profile"])


@router.post("/user-profile", response_model=UserProfileRead, status_code=201)
async def create_user_profile(
    request: Request,
    profile: UserProfileCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserProfileRead:
    """Create a user profile."""
    # Ensure user_id matches current user
    if profile.user_id != current_user["id"]:
        raise NotFoundException("Cannot create profile for another user")
    
    # Check if profile already exists
    existing = await crud_user_profile.get(db=db, user_id=profile.user_id)
    if existing:
        raise NotFoundException("User profile already exists. Use PATCH to update.")
    
    created = await crud_user_profile.create(db=db, object=profile)
    return UserProfileRead(**created) if isinstance(created, dict) else UserProfileRead.model_validate(created)


@router.get("/user-profile/me", response_model=UserProfileRead)
async def get_my_profile(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserProfileRead:
    """Get current user's profile."""
    profile = await crud_user_profile.get(db=db, user_id=current_user["id"], schema_to_select=UserProfileRead)
    if profile is None:
        raise NotFoundException("User profile not found. Create one first.")
    
    return UserProfileRead(**profile) if isinstance(profile, dict) else UserProfileRead.model_validate(profile)


@router.patch("/user-profile/me", response_model=UserProfileRead)
async def update_my_profile(
    request: Request,
    profile_update: UserProfileUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserProfileRead:
    """Update current user's profile."""
    existing = await crud_user_profile.get(db=db, user_id=current_user["id"])
    if existing is None:
        raise NotFoundException("User profile not found. Create one first.")
    
    update_data = profile_update.model_dump(exclude_unset=True)
    if not update_data:
        # Return existing profile if no updates
        existing_read = await crud_user_profile.get(db=db, user_id=current_user["id"], schema_to_select=UserProfileRead)
        return UserProfileRead(**existing_read) if isinstance(existing_read, dict) else UserProfileRead.model_validate(existing_read)
    
    updated = await crud_user_profile.update(db=db, object=update_data, id=existing.id if hasattr(existing, "id") else existing["id"])
    await db.commit()
    
    updated_read = await crud_user_profile.get(db=db, id=existing.id if hasattr(existing, "id") else existing["id"], schema_to_select=UserProfileRead)
    return UserProfileRead(**updated_read) if isinstance(updated_read, dict) else UserProfileRead.model_validate(updated_read)

