from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...models.scheduled_workout import ScheduledWorkout
from ...models.set_entry import SetEntry
from ...models.workout_session import WorkoutSession

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    period: str = Query(default="month", pattern="^(week|month|year|all)$"),
) -> dict[str, Any]:
    """
    Get comprehensive dashboard statistics for the current user.

    Returns aggregated stats including:
    - Total volume (all time and for period)
    - PRs achieved
    - Training frequency
    - Muscle group distribution
    - Progress trends

    **Query Parameters:**
    - `period` (str, default="month"): Time period for stats (week, month, year, all).

    **Returns:**
    - `dict`: Dashboard statistics including volume, PRs, frequency, and trends.
    """
    user_id = current_user["id"]

    # Calculate date range
    end_date = datetime.now()
    if period == "week":
        start_date = end_date - timedelta(weeks=1)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "year":
        start_date = end_date - timedelta(days=365)
    else:  # all
        start_date = datetime(2000, 1, 1)  # Far back date

    # Get workout sessions in period
    sessions_stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.started_at >= start_date)
        .where(WorkoutSession.started_at <= end_date)
        .where(WorkoutSession.completed_at.isnot(None))
    )
    sessions_result = await db.execute(sessions_stmt)
    sessions = sessions_result.scalars().all()

    # Calculate total volume and workout count
    total_volume = 0.0
    workout_count = len(sessions)
    total_sets = 0

    session_ids = [s.id for s in sessions]

    if session_ids:
        # Get all exercise entries for these sessions
        from ...models.exercise_entry import ExerciseEntry

        entries_stmt = select(ExerciseEntry).where(ExerciseEntry.workout_session_id.in_(session_ids))
        entries_result = await db.execute(entries_stmt)
        entries = entries_result.scalars().all()

        entry_ids = [e.id for e in entries]

        if entry_ids:
            # Get all sets for these entries
            sets_stmt = select(SetEntry).where(SetEntry.exercise_entry_id.in_(entry_ids))
            sets_result = await db.execute(sets_stmt)
            sets = sets_result.scalars().all()

            for s in sets:
                if s.weight_kg and s.reps:
                    total_volume += s.weight_kg * s.reps
                total_sets += 1

    # Get all-time stats
    all_time_stmt = (
        select(func.sum(WorkoutSession.total_volume_kg), func.count(WorkoutSession.id))
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.completed_at.isnot(None))
    )
    all_time_result = await db.execute(all_time_stmt)
    all_time_row = all_time_result.first()
    all_time_volume = float(all_time_row[0] or 0)
    all_time_workouts = all_time_row[1] or 0

    # Get upcoming scheduled workouts (next 7 days)
    upcoming_start = datetime.now()
    upcoming_end = datetime.now() + timedelta(days=7)
    scheduled_stmt = (
        select(ScheduledWorkout)
        .where(ScheduledWorkout.user_id == user_id)
        .where(ScheduledWorkout.scheduled_date >= upcoming_start)
        .where(ScheduledWorkout.scheduled_date <= upcoming_end)
        .where(ScheduledWorkout.status == "scheduled")
    )
    scheduled_result = await db.execute(scheduled_stmt)
    upcoming_workouts = len(scheduled_result.scalars().all())

    # Get recent PRs (last 30 days) - simplified version
    # In production, you'd want to track actual PRs in a separate table
    recent_prs = 0  # Placeholder - would need PR tracking logic

    # Calculate training frequency (workouts per week)
    if period == "week":
        workouts_per_week = workout_count
    elif period == "month":
        workouts_per_week = (workout_count / 30) * 7
    elif period == "year":
        workouts_per_week = (workout_count / 365) * 7
    else:
        # For "all", calculate based on account age
        account_age_days = (end_date - start_date).days
        if account_age_days > 0:
            workouts_per_week = (all_time_workouts / account_age_days) * 7
        else:
            workouts_per_week = 0

    # Get today's workout status
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)

    today_sessions_stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.started_at >= today_start)
        .where(WorkoutSession.started_at <= today_end)
    )
    today_sessions_result = await db.execute(today_sessions_stmt)
    today_sessions = today_sessions_result.scalars().all()

    today_workout = None
    if today_sessions:
        today_workout = {
            "id": today_sessions[0].id,
            "name": today_sessions[0].name or "Workout",
            "started_at": today_sessions[0].started_at.isoformat(),
            "completed": today_sessions[0].completed_at is not None,
        }

    return {
        "period": period,
        "period_stats": {
            "total_volume_kg": round(total_volume, 2),
            "workout_count": workout_count,
            "total_sets": total_sets,
            "workouts_per_week": round(workouts_per_week, 1),
        },
        "all_time_stats": {
            "total_volume_kg": round(all_time_volume, 2),
            "total_workouts": all_time_workouts,
        },
        "upcoming": {
            "scheduled_workouts_next_7_days": upcoming_workouts,
        },
        "today": {
            "workout": today_workout,
        },
        "recent_prs": recent_prs,  # Placeholder
    }
