from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .admin.initialize import create_admin_interface
from .api import router

# Rebuild all Pydantic schemas with forward references
# This must happen after all imports to ensure forward references are resolved
try:
    # Import forward reference schemas first
    from .schemas.workout_template import WorkoutTemplateRead
    from .schemas.program import ProgramRead
    from .schemas.workout_session import WorkoutSessionRead
    from .schemas.exercise_entry import ExerciseEntryRead
    from .schemas.set_entry import SetEntryRead
    from .schemas.scheduled_workout import ScheduledWorkoutRead
    
    # Import sys to update module namespaces
    import sys
    
    # Update module namespaces with forward references so Pydantic can resolve them
    # Pydantic looks for forward references in the module where the model is defined
    scheduled_workout_module = sys.modules.get('src.app.schemas.scheduled_workout')
    workout_session_module = sys.modules.get('src.app.schemas.workout_session')
    exercise_entry_module = sys.modules.get('src.app.schemas.exercise_entry')
    
    if scheduled_workout_module:
        scheduled_workout_module.WorkoutTemplateRead = WorkoutTemplateRead
        scheduled_workout_module.ProgramRead = ProgramRead
        scheduled_workout_module.WorkoutSessionRead = WorkoutSessionRead
    
    if workout_session_module:
        workout_session_module.ExerciseEntryRead = ExerciseEntryRead
    
    if exercise_entry_module:
        exercise_entry_module.SetEntryRead = SetEntryRead
    
    # Now rebuild schemas with forward references
    ScheduledWorkoutRead.model_rebuild()
    WorkoutSessionRead.model_rebuild()
    ExerciseEntryRead.model_rebuild()
except Exception:
    pass  # Schemas will be rebuilt when needed
from .core.config import settings
from .core.setup import create_application, lifespan_factory

admin = create_admin_interface()


@asynccontextmanager
async def lifespan_with_admin(app: FastAPI) -> AsyncGenerator[None, None]:
    """Custom lifespan that includes admin initialization."""
    # Get the default lifespan
    default_lifespan = lifespan_factory(settings)

    # Run the default lifespan initialization and our admin initialization
    async with default_lifespan(app):
        # Initialize admin interface if it exists
        if admin:
            try:
                # Initialize admin database and setup
                await admin.initialize()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Admin interface initialization failed, continuing without admin: {e}")

        yield


app = create_application(router=router, settings=settings, lifespan=lifespan_with_admin)

# Add compression middleware (should be first to compress responses)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount admin interface if enabled
if admin:
    app.mount(settings.CRUD_ADMIN_MOUNT_PATH, admin.app)
