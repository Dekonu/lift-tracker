"""Test that all API endpoints can be imported without errors.

This catches import-time errors like:
- Syntax errors in function signatures
- Missing imports
- Forward reference issues
- Dataclass field ordering errors
"""

import pytest


def test_import_workout_sessions_router():
    """Test that workout_sessions router can be imported."""
    try:
        from src.app.api.v1.workout_sessions import router

        assert router is not None
    except Exception as e:
        pytest.fail(f"Failed to import workout_sessions router: {e}")


def test_import_scheduled_workouts_router():
    """Test that scheduled_workouts router can be imported."""
    try:
        from src.app.api.v1.scheduled_workouts import router

        assert router is not None
    except Exception as e:
        pytest.fail(f"Failed to import scheduled_workouts router: {e}")


def test_import_dashboard_router():
    """Test that dashboard router can be imported."""
    try:
        from src.app.api.v1.dashboard import router

        assert router is not None
    except Exception as e:
        pytest.fail(f"Failed to import dashboard router: {e}")


def test_import_programs_router():
    """Test that programs router can be imported."""
    try:
        from src.app.api.v1.programs import router

        assert router is not None
    except Exception as e:
        pytest.fail(f"Failed to import programs router: {e}")


def test_import_set_entries_router():
    """Test that set_entries router can be imported."""
    try:
        from src.app.api.v1.set_entries import router

        assert router is not None
    except Exception as e:
        pytest.fail(f"Failed to import set_entries router: {e}")


def test_import_all_routers():
    """Test that the main API router can import all sub-routers."""
    try:
        from src.app.api.v1 import router

        # Check that router has routes
        assert len(router.routes) > 0
    except Exception as e:
        pytest.fail(f"Failed to import main API router: {e}")


def test_import_main_app():
    """Test that the main FastAPI app can be imported."""
    try:
        from src.app.main import app

        assert app is not None
    except Exception as e:
        pytest.fail(f"Failed to import main app: {e}")
