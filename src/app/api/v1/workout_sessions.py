from datetime import datetime
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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


@router.post("/workout-session", response_model=WorkoutSessionRead, status_code=201)
async def create_workout_session(
    request: Request,
    session: WorkoutSessionCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> WorkoutSessionRead:
    """Create a new workout session."""
    # Ensure user_id matches current user
    if session.user_id != current_user["id"]:
        raise NotFoundException("Cannot create session for another user")
    
    # Auto-generate name if not provided
    session_data = session.model_dump()
    if not session_data.get("name"):
        from datetime import datetime
        started_at = session_data.get("started_at")
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
        elif isinstance(started_at, datetime):
            pass
        else:
            started_at = datetime.now()
        session_data["name"] = f"Workout {started_at.strftime('%Y-%m-%d %H:%M')}"
    
    created = await crud_workout_session.create(db=db, object=session_data)
    await db.commit()
    await db.refresh(created)
    
    return WorkoutSessionRead(**created) if isinstance(created, dict) else WorkoutSessionRead.model_validate(created)


@router.get("/workout-sessions", response_model=PaginatedListResponse[WorkoutSessionRead])
async def get_workout_sessions(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    items_per_page: int = 20,
) -> dict[str, Any]:
    """Get all workout sessions for current user."""
    sessions_data = await crud_workout_session.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=WorkoutSessionRead,
        user_id=current_user["id"],
    )
    
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

    # Fetch exercise entries with sets using a separate query to avoid cartesian product
    stmt = (
        select(ExerciseEntry)
        .where(ExerciseEntry.workout_session_id == session_id)
        .options(selectinload(ExerciseEntry.sets))
        .order_by(ExerciseEntry.order)
    )
    result = await db.execute(stmt)
    exercise_entries = result.scalars().all()

    # Convert to schema format
    exercise_entry_reads = []
    for ee in exercise_entries:
        sets_data = []
        # Access sets via relationship
        sets_list = ee.sets if hasattr(ee, 'sets') else []
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
        }
        entry_read = ExerciseEntryRead(**ee_dict)
        # Add sets to the entry
        if isinstance(entry_read, dict):
            entry_read["sets"] = sets_data
        else:
            entry_read_dict = entry_read.model_dump() if hasattr(entry_read, "model_dump") else dict(entry_read)
            entry_read_dict["sets"] = sets_data
            entry_read = ExerciseEntryRead(**entry_read_dict)
        exercise_entry_reads.append(entry_read)

    # Get session as WorkoutSessionRead schema
    session_read = await crud_workout_session.get(db=db, id=session_id, schema_to_select=WorkoutSessionRead)
    if session_read is None:
        return None

    # Combine session with exercise entries
    if isinstance(session_read, dict):
        session_read["exercise_entries"] = [ee.model_dump() if hasattr(ee, "model_dump") else dict(ee) for ee in exercise_entry_reads]
        return session_read
    else:
        session_dict = session_read.model_dump() if hasattr(session_read, "model_dump") else dict(session_read)
        session_dict["exercise_entries"] = [ee.model_dump() if hasattr(ee, "model_dump") else dict(ee) for ee in exercise_entry_reads]
        return session_dict


@router.get("/workout-session/{session_id}")
async def get_workout_session(
    request: Request,
    session_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, Any]:
    """Get a specific workout session with all entries and sets."""
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
    """Update a workout session."""
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
        
        for entry in entries:
            entry_id = entry.id if hasattr(entry, "id") else entry["id"]
            sets_data = await crud_set_entry.get_multi(
                db=db,
                offset=0,
                limit=1000,
                exercise_entry_id=entry_id,
            )
            sets = sets_data.get("data", [])
            
            for set_obj in sets:
                weight = set_obj.weight_kg if hasattr(set_obj, "weight_kg") else set_obj.get("weight_kg", 0)
                reps = set_obj.reps if hasattr(set_obj, "reps") else set_obj.get("reps", 0)
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
    """Delete a workout session (cascades to entries and sets)."""
    existing = await crud_workout_session.get(db=db, id=session_id, user_id=current_user["id"])
    if existing is None:
        raise NotFoundException("Workout session not found")
    
    await crud_workout_session.db_delete(db=db, id=session_id)
    await db.commit()
    
    return {"message": "Workout session deleted"}


@router.post("/workout-session/{session_id}/exercise-entry", response_model=ExerciseEntryRead, status_code=201)
async def add_exercise_to_session(
    request: Request,
    session_id: int,
    entry: ExerciseEntryCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ExerciseEntryRead:
    """Add an exercise entry to a workout session."""
    # Verify session exists and belongs to user
    session = await crud_workout_session.get(db=db, id=session_id, user_id=current_user["id"])
    if session is None:
        raise NotFoundException("Workout session not found")
    
    # Verify exercise exists
    exercise = await crud_exercises.get(db=db, id=entry.exercise_id)
    if exercise is None:
        raise NotFoundException("Exercise not found")
    
    # Set workout_session_id
    entry_data = entry.model_dump()
    entry_data["workout_session_id"] = session_id
    
    created = await crud_exercise_entry.create(db=db, object=entry_data)
    await db.commit()
    
    return ExerciseEntryRead(**created) if isinstance(created, dict) else ExerciseEntryRead.model_validate(created)


@router.get("/workout-session/{session_id}/exercise-entries", response_model=PaginatedListResponse[ExerciseEntryRead])
async def get_exercise_entries(
    request: Request,
    session_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    items_per_page: int = 50,
) -> dict[str, Any]:
    """Get all exercise entries for a workout session."""
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


@router.post("/exercise-entry/{entry_id}/set", response_model=SetEntryRead, status_code=201)
async def add_set_to_entry(
    request: Request,
    entry_id: int,
    set_entry: SetEntryCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> SetEntryRead:
    """Add a set to an exercise entry."""
    # Verify entry exists and belongs to user's session
    entry = await crud_exercise_entry.get(db=db, id=entry_id)
    if entry is None:
        raise NotFoundException("Exercise entry not found")
    
    entry_session_id = entry.workout_session_id if hasattr(entry, "workout_session_id") else entry["workout_session_id"]
    session = await crud_workout_session.get(db=db, id=entry_session_id, user_id=current_user["id"])
    if session is None:
        raise NotFoundException("Exercise entry not found or access denied")
    
    # Set exercise_entry_id
    set_data = set_entry.model_dump()
    set_data["exercise_entry_id"] = entry_id
    
    created = await crud_set_entry.create(db=db, object=set_data)
    await db.commit()
    
    return SetEntryRead(**created) if isinstance(created, dict) else SetEntryRead.model_validate(created)


@router.get("/exercise-entry/{entry_id}/sets", response_model=PaginatedListResponse[SetEntryRead])
async def get_sets_for_entry(
    request: Request,
    entry_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    items_per_page: int = 50,
) -> dict[str, Any]:
    """Get all sets for an exercise entry."""
    # Verify entry exists and belongs to user's session
    entry = await crud_exercise_entry.get(db=db, id=entry_id)
    if entry is None:
        raise NotFoundException("Exercise entry not found")
    
    entry_session_id = entry.workout_session_id if hasattr(entry, "workout_session_id") else entry["workout_session_id"]
    session = await crud_workout_session.get(db=db, id=entry_session_id, user_id=current_user["id"])
    if session is None:
        raise NotFoundException("Exercise entry not found or access denied")
    
    sets_data = await crud_set_entry.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=SetEntryRead,
        exercise_entry_id=entry_id,
    )
    
    return paginated_response(crud_data=sets_data, page=page, items_per_page=items_per_page)

