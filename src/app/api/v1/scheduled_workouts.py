from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_scheduled_workout import crud_scheduled_workout
from ...crud.crud_workout_template import crud_workout_template
from ...crud.crud_workout_session import crud_workout_session
from ...models.scheduled_workout import ScheduledWorkout
from ...schemas.scheduled_workout import (
    ScheduledWorkoutCreate,
    ScheduledWorkoutRead,
    ScheduledWorkoutUpdate,
)
# Note: Schema rebuilding is handled in src/app/api/v1/__init__.py
# after all modules are imported to ensure forward references are available

router = APIRouter(tags=["scheduled-workouts"])


@router.post("/scheduled-workout", response_model=ScheduledWorkoutRead, status_code=201)
async def create_scheduled_workout(
    request: Request,
    scheduled_workout: ScheduledWorkoutCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ScheduledWorkoutRead:
    """
    Schedule a workout for a specific date.
    
    Creates a scheduled workout that links a workout template to a specific date.
    This can be part of a program or standalone.
    
    **Request Body:**
    - `scheduled_date` (datetime, required): The date and time for the workout.
    - `workout_template_id` (int, required): The workout template to schedule.
    - `program_id` (int, optional): If part of a program.
    - `program_week` (int, optional): Week number in the program.
    - `notes` (str, optional): Notes for this scheduled workout.
    
    **Returns:**
    - `ScheduledWorkoutRead`: The created scheduled workout.
    
    **Raises:**
    - `NotFoundException`: If the workout template is not found.
    """
    # Verify workout template exists
    template = await crud_workout_template.get(db=db, id=scheduled_workout.workout_template_id)
    if template is None:
        raise NotFoundException("Workout template not found")
    
    # Set user_id from current_user
    scheduled_dict = scheduled_workout.model_dump()
    scheduled_dict["user_id"] = current_user["id"]
    scheduled_internal = ScheduledWorkoutCreate(**scheduled_dict)
    
    created = await crud_scheduled_workout.create(db=db, object=scheduled_internal)
    await db.commit()
    await db.refresh(created)
    
    # Fetch with schema
    scheduled_read = await crud_scheduled_workout.get(
        db=db,
        id=created.id,
        schema_to_select=ScheduledWorkoutRead,
        return_as_model=True,
    )
    if scheduled_read is None:
        raise NotFoundException("Created scheduled workout not found")
    
    if isinstance(scheduled_read, dict):
        return ScheduledWorkoutRead(**scheduled_read)
    elif hasattr(scheduled_read, "model_dump"):
        return scheduled_read
    else:
        scheduled_dict = {
            "id": scheduled_read.id,
            "user_id": scheduled_read.user_id,
            "workout_template_id": scheduled_read.workout_template_id,
            "scheduled_date": scheduled_read.scheduled_date,
            "program_id": scheduled_read.program_id,
            "program_week": scheduled_read.program_week,
            "status": scheduled_read.status,
            "completed_workout_session_id": scheduled_read.completed_workout_session_id,
            "notes": scheduled_read.notes,
            "created_at": scheduled_read.created_at,
            "updated_at": scheduled_read.updated_at,
        }
        return ScheduledWorkoutRead(**scheduled_dict)


@router.get("/scheduled-workouts", response_model=PaginatedListResponse[ScheduledWorkoutRead])
async def get_scheduled_workouts(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    status: str | None = None,
    page: int = 1,
    items_per_page: int = 50,
) -> dict[str, Any]:
    """
    Get all scheduled workouts for the current user.
    
    Returns a paginated list of scheduled workouts, optionally filtered by date range and status.
    
    **Query Parameters:**
    - `start_date` (datetime, optional): Filter workouts from this date.
    - `end_date` (datetime, optional): Filter workouts until this date.
    - `status` (str, optional): Filter by status (scheduled, completed, skipped, in_progress).
    - `page` (int, default=1): Page number for pagination.
    - `items_per_page` (int, default=50): Number of items per page.
    
    **Returns:**
    - `PaginatedListResponse[ScheduledWorkoutRead]`: Paginated list of scheduled workouts.
    """
    # Build query with filters
    stmt = select(ScheduledWorkout).where(ScheduledWorkout.user_id == current_user["id"])
    
    if start_date:
        stmt = stmt.where(ScheduledWorkout.scheduled_date >= start_date)
    if end_date:
        stmt = stmt.where(ScheduledWorkout.scheduled_date <= end_date)
    if status:
        stmt = stmt.where(ScheduledWorkout.status == status)
    
    stmt = stmt.order_by(ScheduledWorkout.scheduled_date.asc())
    
    # Get total count
    count_stmt = select(func.count()).select_from(ScheduledWorkout).where(ScheduledWorkout.user_id == current_user["id"])
    if start_date:
        count_stmt = count_stmt.where(ScheduledWorkout.scheduled_date >= start_date)
    if end_date:
        count_stmt = count_stmt.where(ScheduledWorkout.scheduled_date <= end_date)
    if status:
        count_stmt = count_stmt.where(ScheduledWorkout.status == status)
    
    count_result = await db.execute(count_stmt)
    total_count = count_result.scalar() or 0
    
    # Paginate
    stmt = stmt.offset(compute_offset(page, items_per_page)).limit(items_per_page)
    result = await db.execute(stmt)
    scheduled_workouts = result.scalars().all()
    
    # Convert to schema
    scheduled_list = []
    for sw in scheduled_workouts:
        sw_dict = {
            "id": sw.id,
            "user_id": sw.user_id,
            "workout_template_id": sw.workout_template_id,
            "scheduled_date": sw.scheduled_date,
            "program_id": sw.program_id,
            "program_week": sw.program_week,
            "status": sw.status,
            "completed_workout_session_id": sw.completed_workout_session_id,
            "notes": sw.notes,
            "created_at": sw.created_at,
            "updated_at": sw.updated_at,
        }
        scheduled_list.append(ScheduledWorkoutRead(**sw_dict))
    
    scheduled_data = {
        "data": scheduled_list,
        "count": total_count,
    }
    
    return paginated_response(crud_data=scheduled_data, page=page, items_per_page=items_per_page)


@router.get("/scheduled-workout/{scheduled_id}", response_model=ScheduledWorkoutRead)
async def get_scheduled_workout(
    request: Request,
    scheduled_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ScheduledWorkoutRead:
    """
    Get a specific scheduled workout.
    
    **Path Parameters:**
    - `scheduled_id` (int): The ID of the scheduled workout.
    
    **Returns:**
    - `ScheduledWorkoutRead`: The scheduled workout.
    
    **Raises:**
    - `NotFoundException`: If the scheduled workout is not found or doesn't belong to the user.
    """
    scheduled = await crud_scheduled_workout.get(
        db=db,
        id=scheduled_id,
        user_id=current_user["id"],
        schema_to_select=ScheduledWorkoutRead,
    )
    if scheduled is None:
        raise NotFoundException("Scheduled workout not found")
    
    if isinstance(scheduled, dict):
        return ScheduledWorkoutRead(**scheduled)
    elif hasattr(scheduled, "model_dump"):
        return scheduled
    else:
        scheduled_dict = {
            "id": scheduled.id,
            "user_id": scheduled.user_id,
            "workout_template_id": scheduled.workout_template_id,
            "scheduled_date": scheduled.scheduled_date,
            "program_id": scheduled.program_id,
            "program_week": scheduled.program_week,
            "status": scheduled.status,
            "completed_workout_session_id": scheduled.completed_workout_session_id,
            "notes": scheduled.notes,
            "created_at": scheduled.created_at,
            "updated_at": scheduled.updated_at,
        }
        return ScheduledWorkoutRead(**scheduled_dict)


@router.patch("/scheduled-workout/{scheduled_id}", response_model=ScheduledWorkoutRead)
async def update_scheduled_workout(
    request: Request,
    scheduled_id: int,
    update: ScheduledWorkoutUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ScheduledWorkoutRead:
    """
    Update a scheduled workout.
    
    Can update the scheduled date, status, notes, or link to a completed workout session.
    
    **Path Parameters:**
    - `scheduled_id` (int): The ID of the scheduled workout.
    
    **Request Body:**
    - `scheduled_date` (datetime, optional): New scheduled date.
    - `status` (str, optional): New status.
    - `notes` (str, optional): Updated notes.
    - `completed_workout_session_id` (int, optional): Link to completed workout session.
    
    **Returns:**
    - `ScheduledWorkoutRead`: The updated scheduled workout.
    
    **Raises:**
    - `NotFoundException`: If the scheduled workout is not found or doesn't belong to the user.
    """
    # Verify scheduled workout exists and belongs to user
    scheduled = await crud_scheduled_workout.get(db=db, id=scheduled_id, user_id=current_user["id"])
    if scheduled is None:
        raise NotFoundException("Scheduled workout not found")
    
    # Verify completed session belongs to user if provided
    if update.completed_workout_session_id:
        session = await crud_workout_session.get(
            db=db,
            id=update.completed_workout_session_id,
            user_id=current_user["id"],
        )
        if session is None:
            raise NotFoundException("Workout session not found or access denied")
    
    update_dict = update.model_dump(exclude_unset=True)
    updated = await crud_scheduled_workout.update(db=db, object=update_dict, id=scheduled_id)
    await db.commit()
    
    # Fetch updated scheduled workout
    scheduled_read = await crud_scheduled_workout.get(
        db=db,
        id=scheduled_id,
        schema_to_select=ScheduledWorkoutRead,
        return_as_model=True,
    )
    if scheduled_read is None:
        raise NotFoundException("Updated scheduled workout not found")
    
    if isinstance(scheduled_read, dict):
        return ScheduledWorkoutRead(**scheduled_read)
    elif hasattr(scheduled_read, "model_dump"):
        return scheduled_read
    else:
        scheduled_dict = {
            "id": scheduled_read.id,
            "user_id": scheduled_read.user_id,
            "workout_template_id": scheduled_read.workout_template_id,
            "scheduled_date": scheduled_read.scheduled_date,
            "program_id": scheduled_read.program_id,
            "program_week": scheduled_read.program_week,
            "status": scheduled_read.status,
            "completed_workout_session_id": scheduled_read.completed_workout_session_id,
            "notes": scheduled_read.notes,
            "created_at": scheduled_read.created_at,
            "updated_at": scheduled_read.updated_at,
        }
        return ScheduledWorkoutRead(**scheduled_dict)


@router.delete("/scheduled-workout/{scheduled_id}", status_code=204)
async def delete_scheduled_workout(
    request: Request,
    scheduled_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> None:
    """
    Delete a scheduled workout.
    
    **Path Parameters:**
    - `scheduled_id` (int): The ID of the scheduled workout to delete.
    
    **Raises:**
    - `NotFoundException`: If the scheduled workout is not found or doesn't belong to the user.
    """
    scheduled = await crud_scheduled_workout.get(db=db, id=scheduled_id, user_id=current_user["id"])
    if scheduled is None:
        raise NotFoundException("Scheduled workout not found")
    
    await crud_scheduled_workout.db_delete(db=db, id=scheduled_id)
    await db.commit()


@router.post("/program/{program_id}/schedule", response_model=dict[str, Any])
async def schedule_program(
    request: Request,
    program_id: int,
    start_date: datetime,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, Any]:
    """
    Schedule an entire program starting from a specific date.
    
    Creates scheduled workouts for each week in the program based on the program structure.
    
    **Path Parameters:**
    - `program_id` (int): The ID of the program to schedule.
    
    **Query Parameters:**
    - `start_date` (datetime): The start date for the program.
    
    **Returns:**
    - `dict`: Summary of scheduled workouts created.
    
    **Raises:**
    - `NotFoundException`: If the program is not found or doesn't belong to the user.
    """
    from ...crud.crud_program import crud_program
    from ...crud.crud_program_week import crud_program_week
    
    # Verify program exists and belongs to user
    program = await crud_program.get(db=db, id=program_id, user_id=current_user["id"])
    if program is None:
        raise NotFoundException("Program not found")
    
    # Get program weeks
    weeks_data = await crud_program_week.get_multi(
        db=db,
        program_id=program_id,
        limit=1000,
    )
    weeks = weeks_data.get("data", [])
    
    if not weeks:
        raise NotFoundException("Program has no weeks defined")
    
    # Calculate dates for each week
    from datetime import timedelta
    
    scheduled_count = 0
    current_date = start_date
    
    for week in weeks:
        week_number = week.week_number if hasattr(week, "week_number") else week.get("week_number")
        template_id = week.workout_template_id if hasattr(week, "workout_template_id") else week.get("workout_template_id")
        
        if not template_id:
            continue
        
        # Schedule workouts for this week (based on days_per_week)
        program_days_per_week = program.days_per_week if hasattr(program, "days_per_week") else program.get("days_per_week", 3)
        
        for day in range(program_days_per_week):
            scheduled_workout = ScheduledWorkoutCreate(
                user_id=current_user["id"],
                workout_template_id=template_id,
                scheduled_date=current_date,
                program_id=program_id,
                program_week=week_number,
                status="scheduled",
            )
            
            await crud_scheduled_workout.create(db=db, object=scheduled_workout)
            scheduled_count += 1
            current_date += timedelta(days=1)
    
    await db.commit()
    
    return {
        "message": "Program scheduled successfully",
        "program_id": program_id,
        "start_date": start_date.isoformat(),
        "scheduled_workouts_count": scheduled_count,
    }

