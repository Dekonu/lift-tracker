from fastapi import APIRouter

from .analytics import router as analytics_router
from .dashboard import router as dashboard_router
from .equipment import router as equipment_router
from .exercise_equipment import router as exercise_equipment_router
from .exercises import router as exercises_router
from .login import router as login_router
from .logout import router as logout_router
from .muscle_groups import router as muscle_groups_router
from .one_rm import router as one_rm_router
from .posts import router as posts_router
from .programs import router as programs_router
from .rate_limits import router as rate_limits_router
from .tasks import router as tasks_router
from .tiers import router as tiers_router
from .user_profile import router as user_profile_router
from .users import router as users_router
from .scheduled_workouts import router as scheduled_workouts_router
from .set_entries import router as set_entries_router
from .workout_sessions import router as workout_sessions_router
from .workout_templates import router as workout_templates_router
from .workouts import router as workouts_router

# Rebuild schemas with forward references after all imports
# This ensures forward references are resolved before the app starts
try:
    from ...schemas.scheduled_workout import ScheduledWorkoutRead
    from ...schemas.workout_session import WorkoutSessionRead
    from ...schemas.exercise_entry import ExerciseEntryRead
    
    ScheduledWorkoutRead.model_rebuild()
    WorkoutSessionRead.model_rebuild()
    ExerciseEntryRead.model_rebuild()
except Exception:
    pass  # Will be rebuilt when all schemas are loaded

router = APIRouter(prefix="/v1")
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(users_router)
router.include_router(user_profile_router)
router.include_router(posts_router)
router.include_router(tasks_router)
router.include_router(tiers_router)
router.include_router(rate_limits_router)
router.include_router(muscle_groups_router)
router.include_router(exercises_router)
router.include_router(equipment_router)
router.include_router(exercise_equipment_router)
router.include_router(workout_sessions_router)
router.include_router(workout_templates_router)
router.include_router(scheduled_workouts_router)
router.include_router(set_entries_router)
router.include_router(one_rm_router)
router.include_router(programs_router)
router.include_router(analytics_router)
router.include_router(dashboard_router)
router.include_router(workouts_router)
