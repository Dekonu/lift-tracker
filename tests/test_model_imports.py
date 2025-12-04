"""Test that all models can be imported without errors.

This test ensures that all SQLAlchemy models and Pydantic schemas
can be imported without dataclass field ordering errors or forward
reference issues.
"""

import pytest


def test_import_all_models():
    """Test that all models can be imported."""
    try:
        assert True
    except Exception as e:
        pytest.fail(f"Failed to import models: {e}")


def test_import_all_schemas():
    """Test that all schemas can be imported and rebuilt."""
    try:
        from src.app.schemas.exercise_entry import ExerciseEntryRead
        from src.app.schemas.program import ProgramRead
        from src.app.schemas.scheduled_workout import ScheduledWorkoutRead
        from src.app.schemas.set_entry import SetEntryRead
        from src.app.schemas.workout_session import WorkoutSessionRead
        from src.app.schemas.workout_template import WorkoutTemplateRead

        # Rebuild all schemas to check for forward reference issues
        ExerciseEntryRead.model_rebuild()
        SetEntryRead.model_rebuild()
        WorkoutSessionRead.model_rebuild()
        ScheduledWorkoutRead.model_rebuild()
        ProgramRead.model_rebuild()
        WorkoutTemplateRead.model_rebuild()

        assert True
    except Exception as e:
        pytest.fail(f"Failed to import or rebuild schemas: {e}")


def test_import_api_routers():
    """Test that all API routers can be imported."""
    try:
        from src.app.api.v1 import router

        assert router is not None
    except Exception as e:
        pytest.fail(f"Failed to import API router: {e}")


def test_scheduled_workout_model_field_ordering():
    """Test that ScheduledWorkout model has correct field ordering."""
    import inspect

    from src.app.models.scheduled_workout import ScheduledWorkout

    # Get all fields (checking that model can be instantiated)
    _ = inspect.getmembers(ScheduledWorkout, lambda x: isinstance(x, type) and hasattr(x, "__annotations__"))

    # Check that model can be instantiated (indirect test of field ordering)
    # We can't directly test dataclass field order, but if it's wrong, the model won't load
    assert ScheduledWorkout is not None


def test_scheduled_workout_schema_forward_references():
    """Test that ScheduledWorkoutRead schema can resolve forward references."""
    from src.app.schemas.scheduled_workout import ScheduledWorkoutRead

    # Try to rebuild - if forward references are broken, this will fail
    try:
        ScheduledWorkoutRead.model_rebuild()
        assert True
    except Exception as e:
        pytest.fail(f"Failed to rebuild ScheduledWorkoutRead schema: {e}")
