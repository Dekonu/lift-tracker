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
from .scheduled_workouts import router as scheduled_workouts_router
from .set_entries import router as set_entries_router
from .tasks import router as tasks_router
from .tiers import router as tiers_router
from .user_profile import router as user_profile_router
from .users import router as users_router
from .workout_sessions import router as workout_sessions_router
from .workout_templates import router as workout_templates_router
from .workouts import router as workouts_router

# Rebuild schemas with forward references after all imports
# This ensures forward references are resolved before the app starts
try:
    # Import forward reference schemas first
    # Import sys to update module namespaces
    import sys

    from ...schemas.exercise_entry import ExerciseEntryRead
    from ...schemas.program import ProgramRead
    from ...schemas.scheduled_workout import ScheduledWorkoutRead
    from ...schemas.set_entry import SetEntryRead
    from ...schemas.template_exercise_entry import (
        TemplateExerciseEntryCreate,
        TemplateExerciseEntryRead,
    )
    from ...schemas.template_set_entry import TemplateSetEntryCreate, TemplateSetEntryRead
    from ...schemas.workout_session import WorkoutSessionRead
    from ...schemas.workout_template import (
        WorkoutTemplateCreate,
        WorkoutTemplateRead,
    )

    # Update module namespaces with forward references so Pydantic can resolve them
    # Pydantic looks for forward references in the module where the model is defined
    scheduled_workout_module = sys.modules.get("src.app.schemas.scheduled_workout")
    workout_session_module = sys.modules.get("src.app.schemas.workout_session")
    exercise_entry_module = sys.modules.get("src.app.schemas.exercise_entry")
    workout_template_module = sys.modules.get("src.app.schemas.workout_template")
    template_exercise_entry_module = sys.modules.get("src.app.schemas.template_exercise_entry")

    if scheduled_workout_module:
        scheduled_workout_module.WorkoutTemplateRead = WorkoutTemplateRead
        scheduled_workout_module.ProgramRead = ProgramRead
        scheduled_workout_module.WorkoutSessionRead = WorkoutSessionRead

    if workout_session_module:
        workout_session_module.ExerciseEntryRead = ExerciseEntryRead

    if exercise_entry_module:
        exercise_entry_module.SetEntryRead = SetEntryRead

    if workout_template_module:
        workout_template_module.TemplateExerciseEntryCreate = TemplateExerciseEntryCreate
        workout_template_module.TemplateExerciseEntryRead = TemplateExerciseEntryRead

    if template_exercise_entry_module:
        template_exercise_entry_module.TemplateSetEntryCreate = TemplateSetEntryCreate
        template_exercise_entry_module.TemplateSetEntryRead = TemplateSetEntryRead

    # Now rebuild schemas with forward references (rebuild in dependency order)
    # 1. TemplateSetEntryCreate and TemplateSetEntryRead have no forward refs
    TemplateSetEntryCreate.model_rebuild()
    TemplateSetEntryRead.model_rebuild()
    # 2. TemplateExerciseEntryCreate depends on TemplateSetEntryCreate
    #    TemplateExerciseEntryRead depends on TemplateSetEntryRead
    TemplateExerciseEntryCreate.model_rebuild()
    TemplateExerciseEntryRead.model_rebuild()
    # 3. WorkoutTemplateCreate depends on TemplateExerciseEntryCreate
    #    WorkoutTemplateRead depends on TemplateExerciseEntryRead
    WorkoutTemplateCreate.model_rebuild()
    WorkoutTemplateRead.model_rebuild()
    ScheduledWorkoutRead.model_rebuild()
    WorkoutSessionRead.model_rebuild()
    ExerciseEntryRead.model_rebuild()
except Exception as e:
    import logging

    logging.warning(f"Schema rebuild failed, will retry: {e}")
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
