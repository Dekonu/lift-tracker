"""Unit tests for scheduled workout API endpoints."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from src.app.api.v1.scheduled_workouts import (
    create_scheduled_workout,
    get_scheduled_workouts,
    get_scheduled_workout,
    update_scheduled_workout,
    delete_scheduled_workout,
    schedule_program,
)
from src.app.core.exceptions.http_exceptions import NotFoundException
from src.app.schemas.scheduled_workout import ScheduledWorkoutCreate, ScheduledWorkoutUpdate


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def mock_current_user():
    """Mock current user."""
    return {"id": 1, "email": "test@example.com"}


@pytest.fixture
def mock_workout_template():
    """Mock workout template."""
    template = MagicMock()
    template.id = 1
    template.name = "Push Day"
    return template


@pytest.fixture
def mock_scheduled_workout():
    """Mock scheduled workout."""
    workout = MagicMock()
    workout.id = 1
    workout.user_id = 1
    workout.workout_template_id = 1
    workout.scheduled_date = datetime.now()
    workout.program_id = None
    workout.program_week = None
    workout.status = "scheduled"
    workout.completed_workout_session_id = None
    workout.notes = None
    workout.created_at = datetime.now()
    workout.updated_at = None
    return workout


class TestCreateScheduledWorkout:
    """Tests for creating scheduled workouts."""
    
    @pytest.mark.asyncio
    async def test_create_scheduled_workout_success(self, mock_db, mock_current_user, mock_workout_template):
        """Test successful scheduled workout creation."""
        from src.app.crud.crud_workout_template import crud_workout_template
        from src.app.crud.crud_scheduled_workout import crud_scheduled_workout
        
        # Mock template exists
        crud_workout_template.get = AsyncMock(return_value=mock_workout_template)
        
        # Mock scheduled workout creation
        created_workout = MagicMock()
        created_workout.id = 1
        created_workout.user_id = 1
        created_workout.workout_template_id = 1
        created_workout.scheduled_date = datetime.now()
        created_workout.program_id = None
        created_workout.program_week = None
        created_workout.status = "scheduled"
        created_workout.completed_workout_session_id = None
        created_workout.notes = None
        created_workout.created_at = datetime.now()
        created_workout.updated_at = None
        
        crud_scheduled_workout.create = AsyncMock(return_value=created_workout)
        crud_scheduled_workout.get = AsyncMock(return_value={
            "id": 1,
            "user_id": 1,
            "workout_template_id": 1,
            "scheduled_date": datetime.now(),
            "program_id": None,
            "program_week": None,
            "status": "scheduled",
            "completed_workout_session_id": None,
            "notes": None,
            "created_at": datetime.now(),
            "updated_at": None,
        })
        
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        scheduled_data = ScheduledWorkoutCreate(
            scheduled_date=datetime.now(),
            workout_template_id=1,
            status="scheduled",
        )
        
        result = await create_scheduled_workout(
            request=MagicMock(),
            scheduled_workout=scheduled_data,
            db=mock_db,
            current_user=mock_current_user,
        )
        
        assert result is not None
        assert result.id == 1
    
    @pytest.mark.asyncio
    async def test_create_scheduled_workout_template_not_found(self, mock_db, mock_current_user):
        """Test creating scheduled workout with non-existent template."""
        from src.app.crud.crud_workout_template import crud_workout_template
        
        crud_workout_template.get = AsyncMock(return_value=None)
        
        scheduled_data = ScheduledWorkoutCreate(
            scheduled_date=datetime.now(),
            workout_template_id=999,
            status="scheduled",
        )
        
        with pytest.raises(NotFoundException, match="Workout template not found"):
            await create_scheduled_workout(
                request=MagicMock(),
                scheduled_workout=scheduled_data,
                db=mock_db,
                current_user=mock_current_user,
            )


class TestGetScheduledWorkouts:
    """Tests for getting scheduled workouts."""
    
    @pytest.mark.asyncio
    async def test_get_scheduled_workouts_success(self, mock_db, mock_current_user):
        """Test getting scheduled workouts successfully."""
        from src.app.models.scheduled_workout import ScheduledWorkout
        from sqlalchemy import select, func
        
        # Mock workout
        workout = MagicMock()
        workout.id = 1
        workout.user_id = 1
        workout.workout_template_id = 1
        workout.scheduled_date = datetime.now()
        workout.program_id = None
        workout.program_week = None
        workout.status = "scheduled"
        workout.completed_workout_session_id = None
        workout.notes = None
        workout.created_at = datetime.now()
        workout.updated_at = None
        
        # Mock database execution
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [workout]
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Mock count
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1
        mock_db.execute = AsyncMock(side_effect=[mock_result, mock_count_result])
        
        result = await get_scheduled_workouts(
            request=MagicMock(),
            db=mock_db,
            current_user=mock_current_user,
            page=1,
            items_per_page=50,
        )
        
        assert result is not None
        assert "data" in result
        assert "count" in result


class TestGetScheduledWorkout:
    """Tests for getting a single scheduled workout."""
    
    @pytest.mark.asyncio
    async def test_get_scheduled_workout_success(self, mock_db, mock_current_user, mock_scheduled_workout):
        """Test getting a scheduled workout successfully."""
        from src.app.crud.crud_scheduled_workout import crud_scheduled_workout
        
        crud_scheduled_workout.get = AsyncMock(return_value={
            "id": 1,
            "user_id": 1,
            "workout_template_id": 1,
            "scheduled_date": datetime.now(),
            "program_id": None,
            "program_week": None,
            "status": "scheduled",
            "completed_workout_session_id": None,
            "notes": None,
            "created_at": datetime.now(),
            "updated_at": None,
        })
        
        result = await get_scheduled_workout(
            request=MagicMock(),
            scheduled_id=1,
            db=mock_db,
            current_user=mock_current_user,
        )
        
        assert result is not None
        assert result["id"] == 1
    
    @pytest.mark.asyncio
    async def test_get_scheduled_workout_not_found(self, mock_db, mock_current_user):
        """Test getting non-existent scheduled workout."""
        from src.app.crud.crud_scheduled_workout import crud_scheduled_workout
        
        crud_scheduled_workout.get = AsyncMock(return_value=None)
        
        with pytest.raises(NotFoundException, match="Scheduled workout not found"):
            await get_scheduled_workout(
                request=MagicMock(),
                scheduled_id=999,
                db=mock_db,
                current_user=mock_current_user,
            )


class TestUpdateScheduledWorkout:
    """Tests for updating scheduled workouts."""
    
    @pytest.mark.asyncio
    async def test_update_scheduled_workout_success(self, mock_db, mock_current_user, mock_scheduled_workout):
        """Test updating a scheduled workout successfully."""
        from src.app.crud.crud_scheduled_workout import crud_scheduled_workout
        
        crud_scheduled_workout.get = AsyncMock(return_value=mock_scheduled_workout)
        crud_scheduled_workout.update = AsyncMock(return_value=mock_scheduled_workout)
        crud_scheduled_workout.get = AsyncMock(side_effect=[
            mock_scheduled_workout,  # First call for verification
            {  # Second call after update
                "id": 1,
                "user_id": 1,
                "workout_template_id": 1,
                "scheduled_date": datetime.now(),
                "program_id": None,
                "program_week": None,
                "status": "completed",
                "completed_workout_session_id": None,
                "notes": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ])
        
        mock_db.commit = AsyncMock()
        
        update_data = ScheduledWorkoutUpdate(status="completed")
        
        result = await update_scheduled_workout(
            request=MagicMock(),
            scheduled_id=1,
            update=update_data,
            db=mock_db,
            current_user=mock_current_user,
        )
        
        assert result is not None
        assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_update_scheduled_workout_not_found(self, mock_db, mock_current_user):
        """Test updating non-existent scheduled workout."""
        from src.app.crud.crud_scheduled_workout import crud_scheduled_workout
        
        crud_scheduled_workout.get = AsyncMock(return_value=None)
        
        update_data = ScheduledWorkoutUpdate(status="completed")
        
        with pytest.raises(NotFoundException, match="Scheduled workout not found"):
            await update_scheduled_workout(
                request=MagicMock(),
                scheduled_id=999,
                update=update_data,
                db=mock_db,
                current_user=mock_current_user,
            )


class TestDeleteScheduledWorkout:
    """Tests for deleting scheduled workouts."""
    
    @pytest.mark.asyncio
    async def test_delete_scheduled_workout_success(self, mock_db, mock_current_user, mock_scheduled_workout):
        """Test deleting a scheduled workout successfully."""
        from src.app.crud.crud_scheduled_workout import crud_scheduled_workout
        
        crud_scheduled_workout.get = AsyncMock(return_value=mock_scheduled_workout)
        crud_scheduled_workout.db_delete = AsyncMock()
        
        mock_db.commit = AsyncMock()
        
        await delete_scheduled_workout(
            request=MagicMock(),
            scheduled_id=1,
            db=mock_db,
            current_user=mock_current_user,
        )
        
        crud_scheduled_workout.db_delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_scheduled_workout_not_found(self, mock_db, mock_current_user):
        """Test deleting non-existent scheduled workout."""
        from src.app.crud.crud_scheduled_workout import crud_scheduled_workout
        
        crud_scheduled_workout.get = AsyncMock(return_value=None)
        
        with pytest.raises(NotFoundException, match="Scheduled workout not found"):
            await delete_scheduled_workout(
                request=MagicMock(),
                scheduled_id=999,
                db=mock_db,
                current_user=mock_current_user,
            )


class TestScheduleProgram:
    """Tests for scheduling programs."""
    
    @pytest.mark.asyncio
    async def test_schedule_program_success(self, mock_db, mock_current_user):
        """Test scheduling a program successfully."""
        from src.app.crud.crud_program import crud_program
        from src.app.crud.crud_program_week import crud_program_week
        from src.app.crud.crud_scheduled_workout import crud_scheduled_workout
        from datetime import timedelta
        
        # Mock program
        program = MagicMock()
        program.id = 1
        program.user_id = 1
        program.days_per_week = 3
        
        crud_program.get = AsyncMock(return_value=program)
        
        # Mock program weeks
        week = MagicMock()
        week.workout_template_id = 1
        week.week_number = 1
        
        crud_program_week.get_multi = AsyncMock(return_value={
            "data": [week]
        })
        
        crud_scheduled_workout.create = AsyncMock()
        mock_db.commit = AsyncMock()
        
        start_date = datetime.now()
        
        result = await schedule_program(
            request=MagicMock(),
            program_id=1,
            start_date=start_date,
            db=mock_db,
            current_user=mock_current_user,
        )
        
        assert result is not None
        assert "scheduled_workouts_count" in result
        assert result["program_id"] == 1
    
    @pytest.mark.asyncio
    async def test_schedule_program_not_found(self, mock_db, mock_current_user):
        """Test scheduling non-existent program."""
        from src.app.crud.crud_program import crud_program
        
        crud_program.get = AsyncMock(return_value=None)
        
        with pytest.raises(NotFoundException, match="Program not found"):
            await schedule_program(
                request=MagicMock(),
                program_id=999,
                start_date=datetime.now(),
                db=mock_db,
                current_user=mock_current_user,
            )

