from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_exercise import crud_exercises
from ...crud.crud_one_rm import crud_one_rm
from ...schemas.one_rm import OneRMCreate, OneRMRead, OneRMUpdate

router = APIRouter(tags=["one-rm"])


@router.post("/one-rm", response_model=OneRMRead, status_code=201)
async def create_one_rm(
    request: Request,
    one_rm: OneRMCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> OneRMRead:
    """Create or update a 1RM record."""
    # Ensure user_id matches current user
    if one_rm.user_id != current_user["id"]:
        raise NotFoundException("Cannot create 1RM for another user")

    # Verify exercise exists
    exercise = await crud_exercises.get(db=db, id=one_rm.exercise_id)
    if exercise is None:
        raise NotFoundException("Exercise not found")

    # Check if 1RM already exists for this user/exercise
    existing = await crud_one_rm.get(
        db=db,
        user_id=one_rm.user_id,
        exercise_id=one_rm.exercise_id,
    )

    if existing:
        # Update existing
        update_data = one_rm.model_dump(exclude={"user_id", "exercise_id"})
        await crud_one_rm.update(
            db=db,
            object=update_data,
            id=existing.id if hasattr(existing, "id") else existing["id"],
        )
        await db.commit()
        updated_read = await crud_one_rm.get(
            db=db,
            id=existing.id if hasattr(existing, "id") else existing["id"],
            schema_to_select=OneRMRead,
        )
        return OneRMRead(**updated_read) if isinstance(updated_read, dict) else OneRMRead.model_validate(updated_read)
    else:
        # Create new
        created = await crud_one_rm.create(db=db, object=one_rm)
        await db.commit()
        return OneRMRead(**created) if isinstance(created, dict) else OneRMRead.model_validate(created)


@router.get("/one-rm", response_model=PaginatedListResponse[OneRMRead])
async def get_one_rms(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    exercise_id: int | None = None,
    page: int = 1,
    items_per_page: int = 50,
) -> dict[str, Any]:
    """Get all 1RM records for current user, optionally filtered by exercise."""
    filters = {"user_id": current_user["id"]}
    if exercise_id:
        filters["exercise_id"] = exercise_id

    one_rms_data = await crud_one_rm.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=OneRMRead,
        **filters,
    )

    return paginated_response(crud_data=one_rms_data, page=page, items_per_page=items_per_page)


@router.get("/one-rm/{one_rm_id}", response_model=OneRMRead)
async def get_one_rm(
    request: Request,
    one_rm_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> OneRMRead:
    """Get a specific 1RM record."""
    one_rm = await crud_one_rm.get(
        db=db,
        id=one_rm_id,
        schema_to_select=OneRMRead,
        user_id=current_user["id"],
    )
    if one_rm is None:
        raise NotFoundException("1RM record not found")

    return OneRMRead(**one_rm) if isinstance(one_rm, dict) else OneRMRead.model_validate(one_rm)


@router.patch("/one-rm/{one_rm_id}", response_model=OneRMRead)
async def update_one_rm(
    request: Request,
    one_rm_id: int,
    one_rm_update: OneRMUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> OneRMRead:
    """Update a 1RM record."""
    existing = await crud_one_rm.get(db=db, id=one_rm_id, user_id=current_user["id"])
    if existing is None:
        raise NotFoundException("1RM record not found")

    update_data = one_rm_update.model_dump(exclude_unset=True)
    if update_data:
        await crud_one_rm.update(db=db, object=update_data, id=one_rm_id)
        await db.commit()

    updated = await crud_one_rm.get(db=db, id=one_rm_id, schema_to_select=OneRMRead)
    return OneRMRead(**updated) if isinstance(updated, dict) else OneRMRead.model_validate(updated)


@router.delete("/one-rm/{one_rm_id}")
async def delete_one_rm(
    request: Request,
    one_rm_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a 1RM record."""
    existing = await crud_one_rm.get(db=db, id=one_rm_id, user_id=current_user["id"])
    if existing is None:
        raise NotFoundException("1RM record not found")

    await crud_one_rm.db_delete(db=db, id=one_rm_id)
    await db.commit()

    return {"message": "1RM record deleted"}
