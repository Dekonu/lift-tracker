from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_exercise import crud_exercises
from ...crud.crud_exercise_entry import crud_exercise_entry
from ...crud.crud_set_entry import crud_set_entry
from ...crud.crud_workout_session import crud_workout_session
from ...models.exercise_entry import ExerciseEntry
from ...models.set_entry import SetEntry
from ...models.workout_session import WorkoutSession
from ...schemas.exercise_entry import ExerciseEntryCreate, ExerciseEntryRead
from ...schemas.set_entry import SetEntryCreate, SetEntryRead
from ...schemas.workout_session import WorkoutSessionCreate, WorkoutSessionRead, WorkoutSessionUpdate

# Rebuild models to resolve forward references
ExerciseEntryRead.model_rebuild()
WorkoutSessionRead.model_rebuild()

router = APIRouter(tags=["workout-sessions"])


# Define more specific routes first to ensure proper matching
# POST /workout-session/{session_id}/exercise-entry must come before GET /workout-session/{session_id}
@router.post("/workout-session/{session_id}/exercise-entry", response_model=ExerciseEntryRead, status_code=201)
async def add_exercise_to_session(
    request: Request,
    session_id: int,
    entry: ExerciseEntryCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ExerciseEntryRead:
    """
    Add an exercise entry to a workout session.

    Adds an exercise to a workout session. The exercise must exist in the database and the
    session must belong to the authenticated user.

    **Path Parameters:**
    - `session_id` (int): The ID of the workout session.

    **Request Body:**
    - `exercise_id` (int, required): The ID of the exercise to add.
    - `order` (int, default=0): The order of this exercise within the workout.
    - `notes` (str, optional): Notes specific to this exercise entry.

    **Returns:**
    - `ExerciseEntryRead`: The created exercise entry.

    **Raises:**
    - `NotFoundException`: If the session or exercise is not found, or if the session
      doesn't belong to the user.
    """
    # Verify session exists and belongs to user
    session = await crud_workout_session.get(db=db, id=session_id, user_id=current_user["id"])
    if session is None:
        raise NotFoundException("Workout session not found")

    # Verify exercise exists
    exercise = await crud_exercises.get(db=db, id=entry.exercise_id)
    if exercise is None:
        raise NotFoundException("Exercise not found")

    # Set workout_session_id and create Pydantic model
    from ...schemas.exercise_entry import ExerciseEntryCreate

    entry_dict = entry.model_dump()
    entry_dict["workout_session_id"] = session_id
    entry_internal = ExerciseEntryCreate(**entry_dict)

    created = await crud_exercise_entry.create(db=db, object=entry_internal)
    await db.commit()
    await db.refresh(created)

    # Fetch with schema to get proper Pydantic model
    # Use return_as_model=True to get a Pydantic model directly
    entry_read = await crud_exercise_entry.get(
        db=db, id=created.id, schema_to_select=ExerciseEntryRead, return_as_model=True
    )
    if entry_read is None:
        raise NotFoundException("Created exercise entry not found")

    # If it's already a Pydantic model, return it; otherwise convert manually
    # to avoid accessing relationships (which would trigger lazy loading)
    if isinstance(entry_read, dict):
        return ExerciseEntryRead(**entry_read)
    elif hasattr(entry_read, "model_dump"):
        # Already a Pydantic model
        return entry_read
    else:
        # SQLAlchemy model - convert manually, excluding relationships
        # to avoid lazy loading issues
        entry_dict = {
            "id": entry_read.id,
            "workout_session_id": entry_read.workout_session_id,
            "exercise_id": entry_read.exercise_id,
            "order": entry_read.order,
            "notes": entry_read.notes,
            "created_at": entry_read.created_at,
            "sets": [],  # Empty list, sets will be loaded separately if needed
        }
        return ExerciseEntryRead(**entry_dict)


@router.post("/workout-session", response_model=WorkoutSessionRead, status_code=201)
async def create_workout_session(
    request: Request,
    session: WorkoutSessionCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> WorkoutSessionRead:
    """
    Create a new workout session.

    Creates a workout session for the authenticated user. The session name is auto-generated
    from the started_at timestamp if not provided. The user_id is automatically set from the
    authenticated user and cannot be overridden.

    **Request Body:**
    - `started_at` (datetime, optional): When the workout started. Defaults to current time.
    - `name` (str, optional): Name for the workout. Auto-generated if not provided.
    - `notes` (str, optional): Additional notes about the workout.
    - `workout_template_id` (int, optional): ID of the template used for this session.

    **Returns:**
    - `WorkoutSessionRead`: The created workout session with all fields.

    **Raises:**
    - `NotFoundException`: If the created session cannot be found after creation.
    """
    # Set user_id from current_user (ignore any user_id in request for security)
    session_dict = session.model_dump(exclude={"user_id"})
    session_dict["user_id"] = current_user["id"]

    # Auto-generate name if not provided
    if not session_dict.get("name"):
        from datetime import datetime

        started_at = session_dict.get("started_at")
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        elif isinstance(started_at, datetime):
            pass
        else:
            started_at = datetime.now()
        session_dict["name"] = f"Workout {started_at.strftime('%Y-%m-%d %H:%M')}"

    # Create Pydantic model instance for FastCRUD
    from ...schemas.workout_session import WorkoutSessionCreate

    session_internal = WorkoutSessionCreate(**session_dict)
    created = await crud_workout_session.create(db=db, object=session_internal)
    await db.commit()
    await db.refresh(created)

    # Fetch with schema to get proper Pydantic model
    # Use return_as_model=True to get a Pydantic model directly
    session_read = await crud_workout_session.get(
        db=db, id=created.id, schema_to_select=WorkoutSessionRead, return_as_model=True
    )
    if session_read is None:
        raise NotFoundException("Created workout session not found")

    # If it's already a Pydantic model, return it; otherwise convert manually
    # to avoid accessing relationships (which would trigger lazy loading)
    if isinstance(session_read, dict):
        return WorkoutSessionRead(**session_read)
    elif hasattr(session_read, "model_dump"):
        # Already a Pydantic model
        return session_read
    else:
        # SQLAlchemy model - convert manually, excluding relationships
        # to avoid lazy loading issues
        session_dict = {
            "id": session_read.id,
            "user_id": session_read.user_id,
            "name": session_read.name,
            "notes": session_read.notes,
            "started_at": session_read.started_at,
            "completed_at": session_read.completed_at,
            "duration_minutes": session_read.duration_minutes,
            "workout_template_id": session_read.workout_template_id,
            "total_volume_kg": session_read.total_volume_kg,
            "total_sets": session_read.total_sets,
            "created_at": session_read.created_at,
            "updated_at": session_read.updated_at,
            "exercise_entries": [],  # Empty list, entries will be loaded separately if needed
        }
        return WorkoutSessionRead(**session_dict)


@router.get("/workout-sessions", response_model=PaginatedListResponse[WorkoutSessionRead])
async def get_workout_sessions(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    items_per_page: int = 20,
) -> dict[str, Any]:
    """
    Get all workout sessions for the current user.

    Returns a paginated list of workout sessions belonging to the authenticated user.
    Sessions are ordered by most recent first.

    **Query Parameters:**
    - `page` (int, default=1): Page number for pagination.
    - `items_per_page` (int, default=20): Number of items per page.

    **Returns:**
    - `PaginatedListResponse[WorkoutSessionRead]`: Paginated list of workout sessions.
    """
    # Fetch sessions without nested relationships to avoid cartesian product
    # We'll load exercise_entries separately when needed (via get_workout_session endpoint)
    # Use a simple query to avoid loading relationships

    stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == current_user["id"])
        .order_by(WorkoutSession.started_at.desc())
        .offset(compute_offset(page, items_per_page))
        .limit(items_per_page)
    )
    result = await db.execute(stmt)
    sessions = result.scalars().all()

    # Get total count
    count_stmt = select(func.count()).select_from(WorkoutSession).where(WorkoutSession.user_id == current_user["id"])
    count_result = await db.execute(count_stmt)
    total_count = count_result.scalar() or 0

    # Convert to WorkoutSessionRead without loading relationships
    sessions_list = []
    for session in sessions:
        session_dict = {
            "id": session.id,
            "user_id": session.user_id,
            "name": session.name,
            "notes": session.notes,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "duration_minutes": session.duration_minutes,
            "workout_template_id": session.workout_template_id,
            "total_volume_kg": session.total_volume_kg,
            "total_sets": session.total_sets,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "exercise_entries": [],  # Empty to avoid cartesian product
        }
        sessions_list.append(WorkoutSessionRead(**session_dict))

    sessions_data = {"data": sessions_list, "count": total_count}

    return paginated_response(crud_data=sessions_data, page=page, items_per_page=items_per_page)


async def get_workout_session_with_relations(db: AsyncSession, session_id: int, user_id: int) -> dict[str, Any] | None:
    """Get a workout session with all its exercise entries and sets."""
    # First, verify session exists and belongs to user
    session = await crud_workout_session.get(db=db, id=session_id)
    if session is None:
        return None

    # Check ownership
    if isinstance(session, dict):
        session_user_id = session.get("user_id")
    else:
        session_user_id = session.user_id

    if session_user_id != user_id:
        return None

    # Fetch exercise entries without sets to avoid cartesian product
    stmt = select(ExerciseEntry).where(ExerciseEntry.workout_session_id == session_id).order_by(ExerciseEntry.order)
    result = await db.execute(stmt)
    exercise_entries = result.scalars().all()

    # Fetch exercise names for all exercise IDs
    exercise_ids = [ee.exercise_id for ee in exercise_entries]
    exercise_names = {}
    if exercise_ids:
        from ...models.exercise import Exercise

        exercise_stmt = select(Exercise).where(Exercise.id.in_(exercise_ids))
        exercise_result = await db.execute(exercise_stmt)
        exercises = exercise_result.scalars().all()
        exercise_names = {ex.id: ex.name for ex in exercises}

    # Fetch all sets for these entries in a separate query to avoid cartesian product
    entry_ids = [ee.id for ee in exercise_entries]
    sets_by_entry = {}
    if entry_ids:
        sets_stmt = (
            select(SetEntry)
            .where(SetEntry.exercise_entry_id.in_(entry_ids))
            .order_by(SetEntry.exercise_entry_id, SetEntry.set_number)
        )
        sets_result = await db.execute(sets_stmt)
        all_sets = sets_result.scalars().all()
        for s in all_sets:
            if s.exercise_entry_id not in sets_by_entry:
                sets_by_entry[s.exercise_entry_id] = []
            sets_by_entry[s.exercise_entry_id].append(s)

    # Convert to schema format
    exercise_entry_reads = []
    for ee in exercise_entries:
        sets_data = []
        # Get sets from the pre-fetched dictionary
        sets_list = sets_by_entry.get(ee.id, [])
        for s in sets_list:
            set_dict = {
                "id": s.id,
                "exercise_entry_id": s.exercise_entry_id,
                "set_number": s.set_number,
                "weight_kg": s.weight_kg,
                "reps": s.reps,
                "rir": s.rir,
                "rpe": s.rpe,
                "percentage_of_1rm": s.percentage_of_1rm,
                "rest_seconds": s.rest_seconds,
                "tempo": s.tempo,
                "notes": s.notes,
                "is_warmup": s.is_warmup,
                "created_at": s.created_at if hasattr(s, "created_at") else None,
            }
            sets_data.append(set_dict)

        ee_dict = {
            "id": ee.id,
            "workout_session_id": ee.workout_session_id,
            "exercise_id": ee.exercise_id,
            "order": ee.order,
            "notes": ee.notes,
            "created_at": ee.created_at if hasattr(ee, "created_at") else None,
            "exercise_name": exercise_names.get(ee.exercise_id, "Unknown Exercise"),  # Add exercise name
        }
        entry_read = ExerciseEntryRead(**ee_dict)
        # Add sets to the entry
        if isinstance(entry_read, dict):
            entry_read["sets"] = sets_data
            entry_read["exercise_name"] = exercise_names.get(ee.exercise_id, "Unknown Exercise")
        else:
            entry_read_dict = entry_read.model_dump() if hasattr(entry_read, "model_dump") else dict(entry_read)
            entry_read_dict["sets"] = sets_data
            entry_read_dict["exercise_name"] = exercise_names.get(ee.exercise_id, "Unknown Exercise")
            entry_read = ExerciseEntryRead(**entry_read_dict)
        exercise_entry_reads.append(entry_read)

    # Get session as WorkoutSessionRead schema
    session_read = await crud_workout_session.get(db=db, id=session_id, schema_to_select=WorkoutSessionRead)
    if session_read is None:
        return None

    # Combine session with exercise entries
    if isinstance(session_read, dict):
        session_read["exercise_entries"] = [
            ee.model_dump() if hasattr(ee, "model_dump") else dict(ee)
            for ee in exercise_entry_reads
        ]
        return session_read
    else:
        session_dict = session_read.model_dump() if hasattr(session_read, "model_dump") else dict(session_read)
        session_dict["exercise_entries"] = [
            ee.model_dump() if hasattr(ee, "model_dump") else dict(ee)
            for ee in exercise_entry_reads
        ]
        return session_dict


@router.get("/workout-session/{session_id}/exercise-entries", response_model=PaginatedListResponse[ExerciseEntryRead])
async def get_exercise_entries(
    request: Request,
    session_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    items_per_page: int = 50,
) -> dict[str, Any]:
    """
    Get all exercise entries for a workout session.

    Returns a paginated list of exercise entries for a workout session. Only sessions
    belonging to the authenticated user can be accessed.

    **Path Parameters:**
    - `session_id` (int): The ID of the workout session.

    **Query Parameters:**
    - `page` (int, default=1): Page number for pagination.
    - `items_per_page` (int, default=50): Number of items per page.

    **Returns:**
    - `PaginatedListResponse[ExerciseEntryRead]`: Paginated list of exercise entries.

    **Raises:**
    - `NotFoundException`: If the session is not found or doesn't belong to the user.
    """
    # Verify session exists and belongs to user
    session = await crud_workout_session.get(db=db, id=session_id, user_id=current_user["id"])
    if session is None:
        raise NotFoundException("Workout session not found")

    entries_data = await crud_exercise_entry.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=ExerciseEntryRead,
        workout_session_id=session_id,
    )

    return paginated_response(crud_data=entries_data, page=page, items_per_page=items_per_page)


@router.get("/workout-session/{session_id}")
async def get_workout_session(
    request: Request,
    session_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, Any]:
    """
    Get a specific workout session with all entries and sets.

    Retrieves a workout session with all its exercise entries and sets. Only sessions
    belonging to the authenticated user can be accessed.

    **Path Parameters:**
    - `session_id` (int): The ID of the workout session to retrieve.

    **Returns:**
    - `dict[str, Any]`: The workout session with nested exercise entries and sets.

    **Raises:**
    - `NotFoundException`: If the session is not found or doesn't belong to the user.
    """
    session_data = await get_workout_session_with_relations(db=db, session_id=session_id, user_id=current_user["id"])
    if session_data is None:
        raise NotFoundException("Workout session not found")

    return session_data


@router.patch("/workout-session/{session_id}", response_model=WorkoutSessionRead)
async def update_workout_session(
    request: Request,
    session_id: int,
    session_update: WorkoutSessionUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> WorkoutSessionRead:
    """
    Update a workout session.

    Updates a workout session. Only sessions belonging to the authenticated user can be updated.
    If `completed_at` is set, the duration is automatically calculated and total volume/sets are
    recalculated based on all exercise entries and sets.

    **Path Parameters:**
    - `session_id` (int): The ID of the workout session to update.

    **Request Body:**
    - `name` (str, optional): Updated name for the workout.
    - `notes` (str, optional): Updated notes.
    - `started_at` (datetime, optional): Updated start time.
    - `completed_at` (datetime, optional): When the workout was completed.

    **Returns:**
    - `WorkoutSessionRead`: The updated workout session.

    **Raises:**
    - `NotFoundException`: If the session is not found or doesn't belong to the user.
    """
    existing = await crud_workout_session.get(db=db, id=session_id, user_id=current_user["id"])
    if existing is None:
        raise NotFoundException("Workout session not found")

    update_data = session_update.model_dump(exclude_unset=True)

    # Calculate duration if completed_at is set
    if "completed_at" in update_data and update_data["completed_at"]:
        session_obj = await crud_workout_session.get(db=db, id=session_id)
        if session_obj:
            started_at = session_obj.started_at if hasattr(session_obj, "started_at") else session_obj["started_at"]
            completed_at = update_data["completed_at"]
            if isinstance(started_at, datetime) and isinstance(completed_at, datetime):
                duration = int((completed_at - started_at).total_seconds() / 60)
                update_data["duration_minutes"] = duration

    # Calculate total volume and sets
    if update_data.get("completed_at"):
        # Recalculate volume and sets
        exercise_entries = await crud_exercise_entry.get_multi(
            db=db,
            offset=0,
            limit=1000,
            workout_session_id=session_id,
        )
        entries = exercise_entries.get("data", [])

        total_volume = 0.0
        total_sets = 0

        # Use direct query to avoid cartesian product from relationship loading
        entry_ids = [entry.id if hasattr(entry, "id") else entry["id"] for entry in entries]
        if entry_ids:
            stmt = select(SetEntry).where(SetEntry.exercise_entry_id.in_(entry_ids))
            result = await db.execute(stmt)
            all_sets = result.scalars().all()

            for set_obj in all_sets:
                weight = set_obj.weight_kg if hasattr(set_obj, "weight_kg") else 0
                reps = set_obj.reps if hasattr(set_obj, "reps") else 0
                if weight and reps:
                    total_volume += weight * reps
                total_sets += 1

        update_data["total_volume_kg"] = total_volume
        update_data["total_sets"] = total_sets

    if update_data:
        await crud_workout_session.update(db=db, object=update_data, id=session_id)
        await db.commit()

    updated = await crud_workout_session.get(db=db, id=session_id, schema_to_select=WorkoutSessionRead)
    return WorkoutSessionRead(**updated) if isinstance(updated, dict) else WorkoutSessionRead.model_validate(updated)


@router.delete("/workout-session/{session_id}")
async def delete_workout_session(
    request: Request,
    session_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """
    Delete a workout session (cascades to entries and sets).

    Deletes a workout session and all associated exercise entries and sets. Only sessions
    belonging to the authenticated user can be deleted.

    **Path Parameters:**
    - `session_id` (int): The ID of the workout session to delete.

    **Returns:**
    - `dict[str, str]`: Success message.

    **Raises:**
    - `NotFoundException`: If the session is not found or doesn't belong to the user.
    """
    existing = await crud_workout_session.get(db=db, id=session_id, user_id=current_user["id"])
    if existing is None:
        raise NotFoundException("Workout session not found")

    await crud_workout_session.db_delete(db=db, id=session_id)
    await db.commit()

    return {"message": "Workout session deleted"}


@router.post("/exercise-entry/{entry_id}/set", response_model=SetEntryRead, status_code=201)
async def add_set_to_entry(
    request: Request,
    entry_id: int,
    set_entry: SetEntryCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> SetEntryRead:
    """
    Add a set to an exercise entry.

    Adds a set to an exercise entry. The entry must belong to a workout session owned by
    the authenticated user.

    **Path Parameters:**
    - `entry_id` (int): The ID of the exercise entry.

    **Request Body:**
    - `set_number` (int, required): The set number within the exercise entry.
    - `weight_kg` (float, optional): Weight in kilograms.
    - `reps` (int, optional): Number of repetitions.
    - `rir` (int, optional): Reps in Reserve (0-10).
    - `rpe` (float, optional): Rate of Perceived Exertion (1-10).
    - `percentage_of_1rm` (float, optional): Percentage of 1RM used.
    - `rest_seconds` (int, optional): Rest time in seconds.
    - `tempo` (str, optional): Tempo notation (e.g., "2-0-1-0").
    - `notes` (str, optional): Notes for this set.
    - `is_warmup` (bool, default=False): Whether this is a warmup set.

    **Returns:**
    - `SetEntryRead`: The created set entry.

    **Raises:**
    - `NotFoundException`: If the entry is not found or doesn't belong to the user's session.
    """
    # Verify entry exists and belongs to user's session
    entry = await crud_exercise_entry.get(db=db, id=entry_id)
    if entry is None:
        raise NotFoundException("Exercise entry not found")

    entry_session_id = entry.workout_session_id if hasattr(entry, "workout_session_id") else entry["workout_session_id"]
    session = await crud_workout_session.get(db=db, id=entry_session_id, user_id=current_user["id"])
    if session is None:
        raise NotFoundException("Exercise entry not found or access denied")

    # Set exercise_entry_id and create Pydantic model
    from ...schemas.set_entry import SetEntryCreate

    set_dict = set_entry.model_dump()
    set_dict["exercise_entry_id"] = entry_id
    set_internal = SetEntryCreate(**set_dict)

    created = await crud_set_entry.create(db=db, object=set_internal)
    await db.commit()
    await db.refresh(created)

    # Fetch with schema to get proper Pydantic model
    # Use return_as_model=True to get a Pydantic model directly
    set_read = await crud_set_entry.get(db=db, id=created.id, schema_to_select=SetEntryRead, return_as_model=True)
    if set_read is None:
        raise NotFoundException("Created set entry not found")

    # If it's already a Pydantic model, return it; otherwise convert
    if isinstance(set_read, dict):
        return SetEntryRead(**set_read)
    elif hasattr(set_read, "model_dump"):
        # Already a Pydantic model
        return set_read
    else:
        # SQLAlchemy model - convert manually to avoid any relationship issues
        set_dict = {
            "id": set_read.id,
            "exercise_entry_id": set_read.exercise_entry_id,
            "set_number": set_read.set_number,
            "weight_kg": set_read.weight_kg,
            "reps": set_read.reps,
            "rir": set_read.rir,
            "rpe": set_read.rpe,
            "percentage_of_1rm": set_read.percentage_of_1rm,
            "rest_seconds": set_read.rest_seconds,
            "tempo": set_read.tempo,
            "notes": set_read.notes,
            "is_warmup": set_read.is_warmup,
            "created_at": set_read.created_at,
        }
        return SetEntryRead(**set_dict)


@router.get("/exercise-entry/{entry_id}/sets", response_model=PaginatedListResponse[SetEntryRead])
async def get_sets_for_entry(
    request: Request,
    entry_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    items_per_page: int = 50,
) -> dict[str, Any]:
    """
    Get all sets for an exercise entry.

    Returns a paginated list of sets for an exercise entry. The entry must belong to a
    workout session owned by the authenticated user.

    **Path Parameters:**
    - `entry_id` (int): The ID of the exercise entry.

    **Query Parameters:**
    - `page` (int, default=1): Page number for pagination.
    - `items_per_page` (int, default=50): Number of items per page.

    **Returns:**
    - `PaginatedListResponse[SetEntryRead]`: Paginated list of set entries.

    **Raises:**
    - `NotFoundException`: If the entry is not found or doesn't belong to the user's session.
    """
    # Verify entry exists and belongs to user's session
    entry = await crud_exercise_entry.get(db=db, id=entry_id)
    if entry is None:
        raise NotFoundException("Exercise entry not found")

    entry_session_id = entry.workout_session_id if hasattr(entry, "workout_session_id") else entry["workout_session_id"]
    session = await crud_workout_session.get(db=db, id=entry_session_id, user_id=current_user["id"])
    if session is None:
        raise NotFoundException("Exercise entry not found or access denied")

    # Use direct query to avoid cartesian product from relationship loading
    stmt = (
        select(SetEntry)
        .where(SetEntry.exercise_entry_id == entry_id)
        .order_by(SetEntry.set_number)
        .offset(compute_offset(page, items_per_page))
        .limit(items_per_page)
    )
    result = await db.execute(stmt)
    set_models = result.scalars().all()

    # Get total count
    count_stmt = select(func.count()).select_from(SetEntry).where(SetEntry.exercise_entry_id == entry_id)
    count_result = await db.execute(count_stmt)
    total_count = count_result.scalar() or 0

    # Convert to SetEntryRead schema manually to avoid relationship loading
    sets_list = []
    for s in set_models:
        set_dict = {
            "id": s.id,
            "exercise_entry_id": s.exercise_entry_id,
            "set_number": s.set_number,
            "weight_kg": s.weight_kg,
            "reps": s.reps,
            "rir": s.rir,
            "rpe": s.rpe,
            "percentage_of_1rm": s.percentage_of_1rm,
            "rest_seconds": s.rest_seconds,
            "tempo": s.tempo,
            "notes": s.notes,
            "is_warmup": s.is_warmup,
            "created_at": s.created_at if hasattr(s, "created_at") else None,
        }
        sets_list.append(SetEntryRead(**set_dict))

    sets_data = {"data": sets_list, "count": total_count}

    return paginated_response(crud_data=sets_data, page=page, items_per_page=items_per_page)
