from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import ForbiddenException, NotFoundException
from ...crud.crud_exercise import crud_exercises
from ...crud.crud_exercise_instance import crud_exercise_instances
from ...crud.crud_set import crud_sets
from ...crud.crud_workout import crud_workouts
from ...models.exercise_instance import ExerciseInstance
from ...models.set import Set
from ...schemas.exercise_instance import ExerciseInstanceCreate, ExerciseInstanceCreateInternal, ExerciseInstanceRead
from ...schemas.set import SetCreate, SetCreateInternal, SetRead, SetUpdate
from ...schemas.workout import WorkoutCreate, WorkoutCreateInternal, WorkoutRead, WorkoutUpdate

# Rebuild models to resolve forward references for Pydantic v2
# Must rebuild in reverse dependency order (SetRead -> ExerciseInstanceRead -> WorkoutRead)
SetRead.model_rebuild()
ExerciseInstanceRead.model_rebuild()
WorkoutRead.model_rebuild()

router = APIRouter(tags=["workouts"])


async def get_workout_with_relations(db: AsyncSession, workout_id: int, user_id: int) -> WorkoutRead | None:
    """Get a workout with all its relations."""
    # First, verify workout exists and belongs to user (without schema to avoid cartesian product)
    workout = await crud_workouts.get(db=db, id=workout_id)
    if workout is None:
        return None

    # Check ownership
    if isinstance(workout, dict):
        workout_user_id = workout.get("user_id")
    else:
        workout_user_id = workout.user_id

    if workout_user_id != user_id:
        return None

    # Fetch exercise instances with sets using a separate query to avoid cartesian product
    stmt = (
        select(ExerciseInstance)
        .where(ExerciseInstance.workout_id == workout_id)
        .options(selectinload(ExerciseInstance.sets))
        .order_by(ExerciseInstance.order)
    )
    result = await db.execute(stmt)
    exercise_instances = result.scalars().all()

    # Convert to schema format
    exercise_instance_reads = []
    for ei in exercise_instances:
        sets_data = []
        for s in ei.sets:
            set_dict = {
                "id": s.id,
                "exercise_instance_id": s.exercise_instance_id,
                "weight_value": s.weight_value,
                "weight_type": s.weight_type,
                "unit": s.unit,
                "rest_time_seconds": s.rest_time_seconds,
                "rir": s.rir,
                "notes": s.notes,
            }
            sets_data.append(set_dict)

        ei_dict = {
            "id": ei.id,
            "workout_id": ei.workout_id,
            "exercise_id": ei.exercise_id,
            "order": ei.order,
            "sets": sets_data,
        }
        exercise_instance_reads.append(ExerciseInstanceRead(**ei_dict))

    # Get workout as WorkoutRead schema (separate query to avoid cartesian product)
    workout_read = await crud_workouts.get(db=db, id=workout_id, schema_to_select=WorkoutRead)
    if workout_read is None:
        return None

    # Add exercise instances to workout
    if isinstance(workout_read, dict):
        workout_read["exercise_instances"] = exercise_instance_reads
        return WorkoutRead(**workout_read)
    else:
        workout_read.exercise_instances = exercise_instance_reads
        return workout_read


@router.post("/workout", response_model=WorkoutRead, status_code=201)
async def create_workout(
    request: Request,
    workout: WorkoutCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> WorkoutRead:
    """Create a new workout."""
    workout_internal = WorkoutCreateInternal(
        date=workout.date,
        user_id=current_user["id"]
    )
    created = await crud_workouts.create(db=db, object=workout_internal)
    await db.commit()
    await db.refresh(created)
    
    workout_read = await get_workout_with_relations(db=db, workout_id=created.id, user_id=current_user["id"])
    if workout_read is None:
        raise NotFoundException("Created workout not found")

    return cast(WorkoutRead, workout_read)


@router.get("/workouts", response_model=PaginatedListResponse[WorkoutRead])
async def read_workouts(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    items_per_page: int = 20,
) -> dict[str, Any]:
    """Get all workouts for the current user."""
    workouts_data = await crud_workouts.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        user_id=current_user["id"],
    )

    # Add exercise instances to each workout
    workouts = workouts_data.get("data", [])
    for workout in workouts:
        if isinstance(workout, dict):
            workout_id = workout.get("id")
            user_id = workout.get("user_id")
        else:
            workout_id = workout.id
            user_id = workout.user_id
        workout_with_relations = await get_workout_with_relations(db=db, workout_id=workout_id, user_id=user_id)
        if workout_with_relations:
            if isinstance(workout, dict):
                workout["exercise_instances"] = (
                    workout_with_relations.exercise_instances
                    if hasattr(workout_with_relations, "exercise_instances")
                    else workout_with_relations.get("exercise_instances", [])
                )
            else:
                workout.exercise_instances = workout_with_relations.exercise_instances

    response: dict[str, Any] = paginated_response(crud_data=workouts_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/workout/{workout_id}", response_model=WorkoutRead)
async def read_workout(
    request: Request,
    workout_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> WorkoutRead:
    """Get a workout by ID."""
    workout = await get_workout_with_relations(db=db, workout_id=workout_id, user_id=current_user["id"])
    if workout is None:
        raise NotFoundException("Workout not found")

    return cast(WorkoutRead, workout)


@router.patch("/workout/{workout_id}")
async def update_workout(
    request: Request,
    workout_id: int,
    values: WorkoutUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Update a workout."""
    existing = await crud_workouts.get(db=db, id=workout_id)
    if existing is None:
        raise NotFoundException("Workout not found")

    # Check ownership
    if isinstance(existing, dict):
        existing_user_id = existing.get("user_id")
    else:
        existing_user_id = existing.user_id

    if existing_user_id != current_user["id"]:
        raise ForbiddenException("You do not have permission to update this workout")

    await crud_workouts.update(db=db, object=values, id=workout_id)
    return {"message": "Workout updated"}


@router.delete("/workout/{workout_id}")
async def delete_workout(
    request: Request,
    workout_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a workout."""
    existing = await crud_workouts.get(db=db, id=workout_id)
    if existing is None:
        raise NotFoundException("Workout not found")

    # Check ownership
    if isinstance(existing, dict):
        existing_user_id = existing.get("user_id")
    else:
        existing_user_id = existing.user_id

    if existing_user_id != current_user["id"]:
        raise ForbiddenException("You do not have permission to delete this workout")

    await crud_workouts.db_delete(db=db, id=workout_id)
    return {"message": "Workout deleted"}


@router.post("/workout/{workout_id}/exercise-instance", response_model=ExerciseInstanceRead, status_code=201)
async def create_exercise_instance(
    request: Request,
    workout_id: int,
    exercise_instance: ExerciseInstanceCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ExerciseInstanceRead:
    """Add an exercise instance to a workout."""
    # Verify workout exists and belongs to user
    workout = await crud_workouts.get(db=db, id=workout_id)
    if workout is None:
        raise NotFoundException("Workout not found")

    if isinstance(workout, dict):
        workout_user_id = workout.get("user_id")
    else:
        workout_user_id = workout.user_id

    if workout_user_id != current_user["id"]:
        raise ForbiddenException("You do not have permission to modify this workout")

    # Verify exercise exists
    exercise = await crud_exercises.get(db=db, id=exercise_instance.exercise_id)
    if exercise is None:
        raise NotFoundException("Exercise not found")

    exercise_instance_internal = ExerciseInstanceCreateInternal(
        exercise_id=exercise_instance.exercise_id,
        order=exercise_instance.order,
        workout_id=workout_id
    )
    created = await crud_exercise_instances.create(db=db, object=exercise_instance_internal)
    await db.commit()
    await db.refresh(created)

    exercise_instance_read = await crud_exercise_instances.get(
        db=db, id=created.id, schema_to_select=ExerciseInstanceRead
    )
    if exercise_instance_read is None:
        raise NotFoundException("Created exercise instance not found")

    return cast(ExerciseInstanceRead, exercise_instance_read)


@router.delete("/workout/{workout_id}/exercise-instance/{exercise_instance_id}")
async def delete_exercise_instance(
    request: Request,
    workout_id: int,
    exercise_instance_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete an exercise instance from a workout."""
    # Verify workout exists and belongs to user
    workout = await crud_workouts.get(db=db, id=workout_id)
    if workout is None:
        raise NotFoundException("Workout not found")

    if isinstance(workout, dict):
        workout_user_id = workout.get("user_id")
    else:
        workout_user_id = workout.user_id

    if workout_user_id != current_user["id"]:
        raise ForbiddenException("You do not have permission to modify this workout")

    # Verify exercise instance exists and belongs to workout
    exercise_instance = await crud_exercise_instances.get(db=db, id=exercise_instance_id)
    if exercise_instance is None:
        raise NotFoundException("Exercise instance not found")

    if isinstance(exercise_instance, dict):
        ei_workout_id = exercise_instance.get("workout_id")
    else:
        ei_workout_id = exercise_instance.workout_id

    if ei_workout_id != workout_id:
        raise NotFoundException("Exercise instance does not belong to this workout")

    await crud_exercise_instances.db_delete(db=db, id=exercise_instance_id)
    return {"message": "Exercise instance deleted"}


@router.post("/exercise-instance/{exercise_instance_id}/set", response_model=SetRead, status_code=201)
async def create_set(
    request: Request,
    exercise_instance_id: int,
    set_data: SetCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> SetRead:
    """Add a set to an exercise instance."""
    # Verify exercise instance exists and belongs to user's workout
    exercise_instance = await crud_exercise_instances.get(db=db, id=exercise_instance_id)
    if exercise_instance is None:
        raise NotFoundException("Exercise instance not found")

    if isinstance(exercise_instance, dict):
        ei_workout_id = exercise_instance.get("workout_id")
    else:
        ei_workout_id = exercise_instance.workout_id

    workout = await crud_workouts.get(db=db, id=ei_workout_id)
    if workout is None:
        raise NotFoundException("Workout not found")

    if isinstance(workout, dict):
        workout_user_id = workout.get("user_id")
    else:
        workout_user_id = workout.user_id

    if workout_user_id != current_user["id"]:
        raise ForbiddenException("You do not have permission to modify this workout")

    set_internal = SetCreateInternal(
        weight_value=set_data.weight_value,
        weight_type=set_data.weight_type,
        unit=set_data.unit,
        rest_time_seconds=set_data.rest_time_seconds,
        rir=set_data.rir,
        notes=set_data.notes,
        exercise_instance_id=exercise_instance_id
    )
    created = await crud_sets.create(db=db, object=set_internal)
    await db.commit()
    await db.refresh(created)

    set_read = await crud_sets.get(db=db, id=created.id, schema_to_select=SetRead)
    if set_read is None:
        raise NotFoundException("Created set not found")

    return cast(SetRead, set_read)


@router.patch("/set/{set_id}")
async def update_set(
    request: Request,
    set_id: int,
    values: SetUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Update a set."""
    # Verify set exists and belongs to user's workout
    set_obj = await crud_sets.get(db=db, id=set_id)
    if set_obj is None:
        raise NotFoundException("Set not found")

    if isinstance(set_obj, dict):
        ei_id = set_obj.get("exercise_instance_id")
    else:
        ei_id = set_obj.exercise_instance_id

    exercise_instance = await crud_exercise_instances.get(db=db, id=ei_id)
    if exercise_instance is None:
        raise NotFoundException("Exercise instance not found")

    if isinstance(exercise_instance, dict):
        ei_workout_id = exercise_instance.get("workout_id")
    else:
        ei_workout_id = exercise_instance.workout_id

    workout = await crud_workouts.get(db=db, id=ei_workout_id)
    if workout is None:
        raise NotFoundException("Workout not found")

    if isinstance(workout, dict):
        workout_user_id = workout.get("user_id")
    else:
        workout_user_id = workout.user_id

    if workout_user_id != current_user["id"]:
        raise ForbiddenException("You do not have permission to modify this set")

    await crud_sets.update(db=db, object=values, id=set_id)
    return {"message": "Set updated"}


@router.delete("/set/{set_id}")
async def delete_set(
    request: Request,
    set_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a set."""
    # Verify set exists and belongs to user's workout
    set_obj = await crud_sets.get(db=db, id=set_id)
    if set_obj is None:
        raise NotFoundException("Set not found")

    if isinstance(set_obj, dict):
        ei_id = set_obj.get("exercise_instance_id")
    else:
        ei_id = set_obj.exercise_instance_id

    exercise_instance = await crud_exercise_instances.get(db=db, id=ei_id)
    if exercise_instance is None:
        raise NotFoundException("Exercise instance not found")

    if isinstance(exercise_instance, dict):
        ei_workout_id = exercise_instance.get("workout_id")
    else:
        ei_workout_id = exercise_instance.workout_id

    workout = await crud_workouts.get(db=db, id=ei_workout_id)
    if workout is None:
        raise NotFoundException("Workout not found")

    if isinstance(workout, dict):
        workout_user_id = workout.get("user_id")
    else:
        workout_user_id = workout.user_id

    if workout_user_id != current_user["id"]:
        raise ForbiddenException("You do not have permission to delete this set")

    await crud_sets.db_delete(db=db, id=set_id)
    return {"message": "Set deleted"}

