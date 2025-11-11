from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_muscle_group import crud_muscle_groups
from ...schemas.muscle_group import MuscleGroupCreate, MuscleGroupRead, MuscleGroupUpdate

router = APIRouter(tags=["muscle-groups"])


@router.post("/muscle-group", response_model=MuscleGroupRead, status_code=201)
async def create_muscle_group(
    request: Request,
    muscle_group: MuscleGroupCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> MuscleGroupRead:
    """Create a new muscle group."""
    existing = await crud_muscle_groups.exists(db=db, name=muscle_group.name)
    if existing:
        raise DuplicateValueException("Muscle group with this name already exists")

    created = await crud_muscle_groups.create(db=db, object=muscle_group)
    muscle_group_read = await crud_muscle_groups.get(db=db, id=created.id, schema_to_select=MuscleGroupRead)
    if muscle_group_read is None:
        raise NotFoundException("Created muscle group not found")

    return cast(MuscleGroupRead, muscle_group_read)


@router.get("/muscle-groups", response_model=PaginatedListResponse[MuscleGroupRead])
async def read_muscle_groups(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 50,
) -> dict[str, Any]:
    """Get all muscle groups."""
    muscle_groups_data = await crud_muscle_groups.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
    )

    response: dict[str, Any] = paginated_response(
        crud_data=muscle_groups_data, page=page, items_per_page=items_per_page
    )
    return response


@router.get("/muscle-group/{muscle_group_id}", response_model=MuscleGroupRead)
async def read_muscle_group(
    request: Request,
    muscle_group_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> MuscleGroupRead:
    """Get a muscle group by ID."""
    muscle_group = await crud_muscle_groups.get(db=db, id=muscle_group_id, schema_to_select=MuscleGroupRead)
    if muscle_group is None:
        raise NotFoundException("Muscle group not found")

    return cast(MuscleGroupRead, muscle_group)


@router.patch("/muscle-group/{muscle_group_id}")
async def update_muscle_group(
    request: Request,
    muscle_group_id: int,
    values: MuscleGroupUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Update a muscle group."""
    existing = await crud_muscle_groups.get(db=db, id=muscle_group_id)
    if existing is None:
        raise NotFoundException("Muscle group not found")

    if values.name is not None:
        name_exists = await crud_muscle_groups.exists(db=db, name=values.name)
        if name_exists:
            # Check if it's the same muscle group
            existing_with_name = await crud_muscle_groups.get(db=db, name=values.name)
            if isinstance(existing, dict):
                existing_id = existing.get("id")
            else:
                existing_id = existing.id
            if isinstance(existing_with_name, dict):
                existing_name_id = existing_with_name.get("id")
            else:
                existing_name_id = existing_with_name.id
            if existing_name_id != existing_id:
                raise DuplicateValueException("Muscle group with this name already exists")

    await crud_muscle_groups.update(db=db, object=values, id=muscle_group_id)
    return {"message": "Muscle group updated"}


@router.delete("/muscle-group/{muscle_group_id}")
async def delete_muscle_group(
    request: Request,
    muscle_group_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a muscle group."""
    existing = await crud_muscle_groups.get(db=db, id=muscle_group_id)
    if existing is None:
        raise NotFoundException("Muscle group not found")

    await crud_muscle_groups.db_delete(db=db, id=muscle_group_id)
    return {"message": "Muscle group deleted"}

