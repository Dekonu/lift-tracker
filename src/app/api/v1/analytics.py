from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_analytics import crud_strength_progression, crud_volume_tracking
from ...crud.crud_exercise import crud_exercises
from ...crud.crud_exercise_entry import crud_exercise_entry
from ...crud.crud_muscle_group import crud_muscle_groups
from ...crud.crud_set_entry import crud_set_entry
from ...crud.crud_workout_session import crud_workout_session
from ...models.set_entry import SetEntry
from ...models.workout_session import WorkoutSession
from ...schemas.analytics import StrengthProgressionCreate, StrengthProgressionRead, VolumeTrackingCreate, VolumeTrackingRead

router = APIRouter(tags=["analytics"])


@router.get("/analytics/volume", response_model=PaginatedListResponse[VolumeTrackingRead])
async def get_volume_tracking(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    muscle_group_id: int | None = None,
    period_type: str = Query(default="week", pattern="^(week|month|year)$"),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = 1,
    items_per_page: int = 50,
) -> dict[str, Any]:
    """Get volume tracking data for the current user.
    
    If no dates provided, defaults to last 4 weeks.
    """
    if not start_date:
        end_date = end_date or datetime.now()
        if period_type == "week":
            start_date = end_date - timedelta(weeks=4)
        elif period_type == "month":
            start_date = end_date - timedelta(days=120)
        else:  # year
            start_date = end_date - timedelta(days=365)
    
    filters = {
        "user_id": current_user["id"],
        "period_type": period_type,
    }
    if muscle_group_id:
        filters["muscle_group_id"] = muscle_group_id
    
    volume_data = await crud_volume_tracking.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=VolumeTrackingRead,
        **filters,
    )
    
    return paginated_response(crud_data=volume_data, page=page, items_per_page=items_per_page)


@router.post("/analytics/volume/calculate", response_model=dict[str, Any])
async def calculate_volume_tracking(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    period_type: str = Query(default="week", pattern="^(week|month|year)$"),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[str, Any]:
    """Calculate and store volume tracking for a time period.
    
    This aggregates volume from workout sessions and stores it in volume_tracking table.
    """
    if not start_date or not end_date:
        end_date = datetime.now()
        if period_type == "week":
            start_date = end_date - timedelta(weeks=1)
        elif period_type == "month":
            start_date = end_date - timedelta(days=30)
        else:  # year
            start_date = end_date - timedelta(days=365)
    
    # Get all workout sessions in the period
    sessions_data = await crud_workout_session.get_multi(
        db=db,
        offset=0,
        limit=10000,
        user_id=current_user["id"],
    )
    sessions = sessions_data.get("data", [])
    
    # Filter sessions by date range
    filtered_sessions = []
    for session in sessions:
        started_at = session.started_at if hasattr(session, "started_at") else session.get("started_at")
        if isinstance(started_at, datetime) and start_date <= started_at <= end_date:
            filtered_sessions.append(session)
    
    # Aggregate volume by muscle group
    muscle_group_volume: dict[int, dict[str, Any]] = {}
    
    for session in filtered_sessions:
        session_id = session.id if hasattr(session, "id") else session["id"]
        
        # Get exercise entries
        entries_data = await crud_exercise_entry.get_multi(
            db=db,
            offset=0,
            limit=1000,
            workout_session_id=session_id,
        )
        entries = entries_data.get("data", [])
        
        for entry in entries:
            exercise_id = entry.exercise_id if hasattr(entry, "exercise_id") else entry["exercise_id"]
            entry_id = entry.id if hasattr(entry, "id") else entry["id"]
            
            # Get exercise to find muscle groups
            exercise = await crud_exercises.get(db=db, id=exercise_id)
            if not exercise:
                continue
            
            primary_muscle_ids = exercise.primary_muscle_group_ids if hasattr(exercise, "primary_muscle_group_ids") else exercise.get("primary_muscle_group_ids", [])
            secondary_muscle_ids = exercise.secondary_muscle_group_ids if hasattr(exercise, "secondary_muscle_group_ids") else exercise.get("secondary_muscle_group_ids", [])
            
            # Get sets for this entry
            sets_data = await crud_set_entry.get_multi(
                db=db,
                offset=0,
                limit=1000,
                exercise_entry_id=entry_id,
            )
            sets = sets_data.get("data", [])
            
            # Calculate volume for this exercise
            exercise_volume = 0.0
            exercise_sets = 0
            exercise_reps = 0
            
            for set_obj in sets:
                weight = set_obj.weight_kg if hasattr(set_obj, "weight_kg") else set_obj.get("weight_kg", 0)
                reps = set_obj.reps if hasattr(set_obj, "reps") else set_obj.get("reps", 0)
                if weight and reps:
                    exercise_volume += weight * reps
                    exercise_reps += reps
                exercise_sets += 1
            
            # Add to muscle group totals
            all_muscle_ids = list(set(primary_muscle_ids + secondary_muscle_ids))
            for muscle_id in all_muscle_ids:
                if muscle_id not in muscle_group_volume:
                    muscle_group_volume[muscle_id] = {
                        "total_volume_kg": 0.0,
                        "total_sets": 0,
                        "total_reps": 0,
                    }
                muscle_group_volume[muscle_id]["total_volume_kg"] += exercise_volume
                muscle_group_volume[muscle_id]["total_sets"] += exercise_sets
                muscle_group_volume[muscle_id]["total_reps"] += exercise_reps
    
    # Create or update volume tracking records
    created_count = 0
    updated_count = 0
    
    for muscle_id, volume_data in muscle_group_volume.items():
        # Check if record exists
        existing = await crud_volume_tracking.get(
            db=db,
            user_id=current_user["id"],
            muscle_group_id=muscle_id,
            period_type=period_type,
        )
        
        volume_tracking_data = VolumeTrackingCreate(
            user_id=current_user["id"],
            muscle_group_id=muscle_id,
            period_start=start_date,
            period_end=end_date,
            period_type=period_type,
            total_volume_kg=volume_data["total_volume_kg"],
            total_sets=volume_data["total_sets"],
            total_reps=volume_data["total_reps"],
        )
        
        if existing:
            # Update existing
            await crud_volume_tracking.update(
                db=db,
                object=volume_tracking_data.model_dump(exclude={"user_id", "muscle_group_id", "period_start", "period_end", "period_type"}),
                id=existing.id if hasattr(existing, "id") else existing["id"],
            )
            updated_count += 1
        else:
            # Create new
            await crud_volume_tracking.create(db=db, object=volume_tracking_data)
            created_count += 1
    
    await db.commit()
    
    return {
        "message": "Volume tracking calculated",
        "period_type": period_type,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "muscle_groups_processed": len(muscle_group_volume),
        "records_created": created_count,
        "records_updated": updated_count,
    }


@router.get("/analytics/strength-progression", response_model=PaginatedListResponse[StrengthProgressionRead])
async def get_strength_progression(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    exercise_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = 1,
    items_per_page: int = 50,
) -> dict[str, Any]:
    """Get strength progression data for the current user."""
    filters = {"user_id": current_user["id"]}
    if exercise_id:
        filters["exercise_id"] = exercise_id
    
    progression_data = await crud_strength_progression.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=StrengthProgressionRead,
        **filters,
    )
    
    return paginated_response(crud_data=progression_data, page=page, items_per_page=items_per_page)


@router.post("/analytics/strength-progression/calculate", response_model=dict[str, Any])
async def calculate_strength_progression(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    exercise_id: int,
    date: datetime | None = None,
) -> dict[str, Any]:
    """Calculate strength progression for an exercise from recent workout sessions.
    
    This analyzes sets from workout sessions to estimate 1RM and track volume.
    """
    if not date:
        date = datetime.now()
    
    # Verify exercise exists
    exercise = await crud_exercises.get(db=db, id=exercise_id)
    if exercise is None:
        raise NotFoundException("Exercise not found")
    
    # Get recent workout sessions (last 30 days)
    start_date = date - timedelta(days=30)
    sessions_data = await crud_workout_session.get_multi(
        db=db,
        offset=0,
        limit=1000,
        user_id=current_user["id"],
    )
    sessions = sessions_data.get("data", [])
    
    # Find sessions with this exercise
    total_volume = 0.0
    total_rpe = 0.0
    rpe_count = 0
    max_estimated_1rm = 0.0
    
    for session in sessions:
        session_started = session.started_at if hasattr(session, "started_at") else session.get("started_at")
        if not isinstance(session_started, datetime) or session_started < start_date:
            continue
        
        session_id = session.id if hasattr(session, "id") else session["id"]
        
        # Get exercise entries for this exercise
        entries_data = await crud_exercise_entry.get_multi(
            db=db,
            offset=0,
            limit=1000,
            workout_session_id=session_id,
            exercise_id=exercise_id,
        )
        entries = entries_data.get("data", [])
        
        for entry in entries:
            entry_id = entry.id if hasattr(entry, "id") else entry["id"]
            
            # Get sets
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
                rpe = set_obj.rpe if hasattr(set_obj, "rpe") else set_obj.get("rpe")
                percentage = set_obj.percentage_of_1rm if hasattr(set_obj, "percentage_of_1rm") else set_obj.get("percentage_of_1rm")
                
                if weight and reps:
                    total_volume += weight * reps
                    
                    # Estimate 1RM using Epley formula: 1RM = weight × (1 + reps/30)
                    estimated_1rm = weight * (1 + reps / 30)
                    max_estimated_1rm = max(max_estimated_1rm, estimated_1rm)
                
                if rpe:
                    total_rpe += rpe
                    rpe_count += 1
    
    average_rpe = total_rpe / rpe_count if rpe_count > 0 else None
    
    # Create or update strength progression record
    progression_data = StrengthProgressionCreate(
        user_id=current_user["id"],
        exercise_id=exercise_id,
        date=date,
        estimated_1rm_kg=max_estimated_1rm if max_estimated_1rm > 0 else 0.0,
        volume_kg=total_volume,
        average_rpe=average_rpe,
    )
    
    # Check if record exists for this date
    existing = await crud_strength_progression.get(
        db=db,
        user_id=current_user["id"],
        exercise_id=exercise_id,
    )
    
    if existing:
        # Update existing (or create new for this date)
        await crud_strength_progression.create(db=db, object=progression_data)
    else:
        await crud_strength_progression.create(db=db, object=progression_data)
    
    await db.commit()
    
    return {
        "message": "Strength progression calculated",
        "exercise_id": exercise_id,
        "date": date.isoformat(),
        "estimated_1rm_kg": max_estimated_1rm,
        "volume_kg": total_volume,
        "average_rpe": average_rpe,
    }

