from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_exercise import (
    create_exercise_with_muscle_groups,
    crud_exercises,
    get_exercise_with_muscle_groups,
    update_exercise_with_muscle_groups,
)
from ...crud.crud_muscle_group import crud_muscle_groups
from ...schemas.exercise import ExerciseCreate, ExerciseRead, ExerciseUpdate

router = APIRouter(tags=["exercises"])


@router.post("/exercise", response_model=ExerciseRead, status_code=201)
async def create_exercise(
    request: Request,
    exercise: ExerciseCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ExerciseRead:
    """Create a new exercise."""
    # Check if exercise name already exists
    existing = await crud_exercises.exists(db=db, name=exercise.name)
    if existing:
        raise DuplicateValueException("Exercise with this name already exists")

    # Validate primary muscle group exists
    primary_mg = await crud_muscle_groups.get(db=db, id=exercise.primary_muscle_group_id)
    if primary_mg is None:
        raise NotFoundException("Primary muscle group not found")

    # Validate secondary muscle groups exist
    if exercise.secondary_muscle_group_ids:
        for mg_id in exercise.secondary_muscle_group_ids:
            mg = await crud_muscle_groups.get(db=db, id=mg_id)
            if mg is None:
                raise NotFoundException(f"Secondary muscle group with ID {mg_id} not found")

    created = await create_exercise_with_muscle_groups(db=db, exercise_data=exercise)
    return cast(ExerciseRead, created)


@router.get("/exercises", response_model=PaginatedListResponse[ExerciseRead])
async def read_exercises(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 50,
) -> dict[str, Any]:
    """Get all exercises."""
    exercises_data = await crud_exercises.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
    )

    # For each exercise, add secondary muscle group IDs
    exercises = exercises_data.get("data", [])
    for exercise in exercises:
        if isinstance(exercise, dict):
            exercise_id = exercise.get("id")
        else:
            exercise_id = exercise.id
        exercise_with_mg = await get_exercise_with_muscle_groups(db=db, exercise_id=exercise_id)
        if exercise_with_mg:
            secondary_ids = exercise_with_mg.secondary_muscle_group_ids
            if isinstance(exercise, dict):
                exercise["secondary_muscle_group_ids"] = secondary_ids
            else:
                exercise.secondary_muscle_group_ids = secondary_ids

    response: dict[str, Any] = paginated_response(crud_data=exercises_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/exercise/{exercise_id}", response_model=ExerciseRead)
async def read_exercise(
    request: Request,
    exercise_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ExerciseRead:
    """Get an exercise by ID."""
    exercise = await get_exercise_with_muscle_groups(db=db, exercise_id=exercise_id)
    if exercise is None:
        raise NotFoundException("Exercise not found")

    return cast(ExerciseRead, exercise)


@router.patch("/exercise/{exercise_id}")
async def update_exercise(
    request: Request,
    exercise_id: int,
    values: ExerciseUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Update an exercise."""
    existing = await crud_exercises.get(db=db, id=exercise_id)
    if existing is None:
        raise NotFoundException("Exercise not found")

    # Check if new name conflicts
    if values.name is not None:
        name_exists = await crud_exercises.exists(db=db, name=values.name)
        if name_exists:
            existing_with_name = await crud_exercises.get(db=db, name=values.name)
            if isinstance(existing, dict):
                existing_id = existing.get("id")
            else:
                existing_id = existing.id
            if isinstance(existing_with_name, dict):
                existing_name_id = existing_with_name.get("id")
            else:
                existing_name_id = existing_with_name.id
            if existing_name_id != existing_id:
                raise DuplicateValueException("Exercise with this name already exists")

    # Validate primary muscle group if provided
    if values.primary_muscle_group_id is not None:
        primary_mg = await crud_muscle_groups.get(db=db, id=values.primary_muscle_group_id)
        if primary_mg is None:
            raise NotFoundException("Primary muscle group not found")

    # Validate secondary muscle groups if provided
    if values.secondary_muscle_group_ids is not None:
        for mg_id in values.secondary_muscle_group_ids:
            mg = await crud_muscle_groups.get(db=db, id=mg_id)
            if mg is None:
                raise NotFoundException(f"Secondary muscle group with ID {mg_id} not found")

    await update_exercise_with_muscle_groups(db=db, exercise_id=exercise_id, exercise_data=values)
    return {"message": "Exercise updated"}


@router.delete("/exercise/{exercise_id}")
async def delete_exercise(
    request: Request,
    exercise_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete an exercise."""
    existing = await crud_exercises.get(db=db, id=exercise_id)
    if existing is None:
        raise NotFoundException("Exercise not found")

    await crud_exercises.db_delete(db=db, id=exercise_id)
    return {"message": "Exercise deleted"}

