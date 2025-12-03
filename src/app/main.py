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
    from .schemas.scheduled_workout import ScheduledWorkoutRead
    from .schemas.workout_session import WorkoutSessionRead
    from .schemas.exercise_entry import ExerciseEntryRead
    
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
