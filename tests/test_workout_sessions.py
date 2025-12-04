"""Unit tests for workout session API endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.app.api.v1.workout_sessions import (
    add_exercise_to_session,
    add_set_to_entry,
    create_workout_session,
    delete_workout_session,
    get_exercise_entries,
    get_sets_for_entry,
    get_workout_session,
    get_workout_sessions,
    update_workout_session,
)
from src.app.core.exceptions.http_exceptions import NotFoundException
from src.app.schemas.exercise_entry import ExerciseEntryCreate, ExerciseEntryRead
from src.app.schemas.set_entry import SetEntryCreate, SetEntryRead
from src.app.schemas.workout_session import WorkoutSessionCreate, WorkoutSessionRead, WorkoutSessionUpdate


class TestCreateWorkoutSession:
    """Test workout session creation endpoint."""

    @pytest.mark.asyncio
    async def test_create_workout_session_success(self, mock_db, current_user_dict):
        """Test successful workout session creation."""
        started_at = datetime.now(UTC)
        session_create = WorkoutSessionCreate(started_at=started_at)
        created_mock = Mock(id=1)
        session_read = WorkoutSessionRead(
            id=1,
            user_id=current_user_dict["id"],
            name="Workout 2024-01-15 10:00",
            started_at=started_at,
            completed_at=None,
            duration_minutes=None,
            workout_template_id=None,
            total_volume_kg=None,
            total_sets=None,
            created_at=started_at,
            updated_at=None,
            exercise_entries=[],
        )

        with patch("src.app.api.v1.workout_sessions.crud_workout_session") as mock_crud:
            mock_crud.create = AsyncMock(return_value=created_mock)
            mock_crud.get = AsyncMock(return_value=session_read)

            result = await create_workout_session(Mock(), session_create, mock_db, current_user_dict)

            assert result.id == 1
            assert result.user_id == current_user_dict["id"]
            mock_crud.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_workout_session_not_found_after_creation(self, mock_db, current_user_dict):
        """Test workout session creation when session not found after creation."""
        session_create = WorkoutSessionCreate(started_at=datetime.now(UTC))
        created_mock = Mock(id=1)

        with patch("src.app.api.v1.workout_sessions.crud_workout_session") as mock_crud:
            mock_crud.create = AsyncMock(return_value=created_mock)
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Created workout session not found"):
                await create_workout_session(Mock(), session_create, mock_db, current_user_dict)


class TestGetWorkoutSessions:
    """Test workout sessions list endpoint."""

    @pytest.mark.asyncio
    async def test_get_workout_sessions_success(self, mock_db, current_user_dict):
        """Test successful workout sessions list retrieval."""
        from unittest.mock import MagicMock

        # Mock session object
        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.user_id = current_user_dict["id"]
        mock_session.name = "Test Workout"
        mock_session.notes = None
        mock_session.started_at = datetime.now(UTC)
        mock_session.completed_at = None
        mock_session.duration_minutes = None
        mock_session.workout_template_id = None
        mock_session.total_volume_kg = None
        mock_session.total_sets = None
        mock_session.created_at = datetime.now(UTC)
        mock_session.updated_at = None

        # Mock result object
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_session]

        # Mock count result
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        # Mock db.execute to return different values for query and count
        mock_db.execute = AsyncMock(side_effect=[mock_result, mock_count_result])

        result = await get_workout_sessions(Mock(), mock_db, current_user_dict, page=1, items_per_page=20)

        assert result is not None
        assert "data" in result
        # paginated_response returns total_count, has_more, page, items_per_page, not "pagination"
        assert "total_count" in result or "pagination" in result


class TestGetWorkoutSession:
    """Test workout session retrieval endpoint."""

    @pytest.mark.asyncio
    async def test_get_workout_session_success(self, mock_db, current_user_dict):
        """Test successful workout session retrieval."""
        session_id = 1
        session_data = {
            "id": session_id,
            "user_id": current_user_dict["id"],
            "name": "Test Workout",
            "exercise_entries": [],
        }

        with patch("src.app.api.v1.workout_sessions.get_workout_session_with_relations") as mock_get:
            mock_get.return_value = session_data

            result = await get_workout_session(Mock(), session_id, mock_db, current_user_dict)

            assert result == session_data
            mock_get.assert_called_once_with(db=mock_db, session_id=session_id, user_id=current_user_dict["id"])

    @pytest.mark.asyncio
    async def test_get_workout_session_not_found(self, mock_db, current_user_dict):
        """Test workout session retrieval when not found."""
        session_id = 999

        with patch("src.app.api.v1.workout_sessions.get_workout_session_with_relations") as mock_get:
            mock_get.return_value = None

            with pytest.raises(NotFoundException, match="Workout session not found"):
                await get_workout_session(Mock(), session_id, mock_db, current_user_dict)


class TestUpdateWorkoutSession:
    """Test workout session update endpoint."""

    @pytest.mark.asyncio
    async def test_update_workout_session_success(self, mock_db, current_user_dict):
        """Test successful workout session update."""
        session_id = 1
        session_update = WorkoutSessionUpdate(name="Updated Workout")
        existing = {"id": 1, "user_id": current_user_dict["id"]}
        started_at = datetime.now(UTC)
        updated = WorkoutSessionRead(
            id=1,
            user_id=current_user_dict["id"],
            name="Updated Workout",
            started_at=started_at,
            completed_at=None,
            duration_minutes=None,
            workout_template_id=None,
            total_volume_kg=None,
            total_sets=None,
            created_at=started_at,
            updated_at=None,
            exercise_entries=[],
        )

        with patch("src.app.api.v1.workout_sessions.crud_workout_session") as mock_crud:
            mock_crud.get = AsyncMock(return_value=existing)
            mock_crud.update = AsyncMock(return_value=None)
            mock_crud.get.return_value = updated

            result = await update_workout_session(Mock(), session_id, session_update, mock_db, current_user_dict)

            assert result.name == "Updated Workout"
            mock_crud.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_workout_session_not_found(self, mock_db, current_user_dict):
        """Test workout session update when not found."""
        session_id = 999
        session_update = WorkoutSessionUpdate(name="Updated Workout")

        with patch("src.app.api.v1.workout_sessions.crud_workout_session") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Workout session not found"):
                await update_workout_session(Mock(), session_id, session_update, mock_db, current_user_dict)


class TestDeleteWorkoutSession:
    """Test workout session deletion endpoint."""

    @pytest.mark.asyncio
    async def test_delete_workout_session_success(self, mock_db, current_user_dict):
        """Test successful workout session deletion."""
        session_id = 1
        existing = {"id": 1, "user_id": current_user_dict["id"]}

        with patch("src.app.api.v1.workout_sessions.crud_workout_session") as mock_crud:
            mock_crud.get = AsyncMock(return_value=existing)
            mock_crud.db_delete = AsyncMock(return_value=None)

            result = await delete_workout_session(Mock(), session_id, mock_db, current_user_dict)

            assert result == {"message": "Workout session deleted"}
            mock_crud.db_delete.assert_called_once_with(db=mock_db, id=session_id)

    @pytest.mark.asyncio
    async def test_delete_workout_session_not_found(self, mock_db, current_user_dict):
        """Test workout session deletion when not found."""
        session_id = 999

        with patch("src.app.api.v1.workout_sessions.crud_workout_session") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Workout session not found"):
                await delete_workout_session(Mock(), session_id, mock_db, current_user_dict)


class TestAddExerciseToSession:
    """Test exercise entry creation endpoint."""

    @pytest.mark.asyncio
    async def test_add_exercise_to_session_success(self, mock_db, current_user_dict):
        """Test successful exercise entry creation."""
        session_id = 1
        entry_create = ExerciseEntryCreate(exercise_id=1, workout_session_id=session_id, order=0)
        session = {"id": 1, "user_id": current_user_dict["id"]}
        exercise = {"id": 1, "name": "Bench Press"}
        created_mock = Mock(id=1)
        entry_read = ExerciseEntryRead(
            id=1,
            workout_session_id=session_id,
            exercise_id=1,
            order=0,
            created_at=datetime.now(UTC),
            sets=[],
        )

        with (
            patch("src.app.api.v1.workout_sessions.crud_workout_session") as mock_crud_w,
            patch("src.app.api.v1.workout_sessions.crud_exercises") as mock_crud_ex,
            patch("src.app.api.v1.workout_sessions.crud_exercise_entry") as mock_crud_ei,
        ):
            mock_crud_w.get = AsyncMock(return_value=session)
            mock_crud_ex.get = AsyncMock(return_value=exercise)
            mock_crud_ei.create = AsyncMock(return_value=created_mock)
            mock_crud_ei.get = AsyncMock(return_value=entry_read)

            result = await add_exercise_to_session(Mock(), session_id, entry_create, mock_db, current_user_dict)

            assert result.id == 1
            assert result.workout_session_id == session_id

    @pytest.mark.asyncio
    async def test_add_exercise_to_session_workout_not_found(self, mock_db, current_user_dict):
        """Test exercise entry creation when session not found."""
        session_id = 999
        entry_create = ExerciseEntryCreate(exercise_id=1, workout_session_id=session_id, order=0)

        with patch("src.app.api.v1.workout_sessions.crud_workout_session") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Workout session not found"):
                await add_exercise_to_session(Mock(), session_id, entry_create, mock_db, current_user_dict)

    @pytest.mark.asyncio
    async def test_add_exercise_to_session_exercise_not_found(self, mock_db, current_user_dict):
        """Test exercise entry creation when exercise not found."""
        session_id = 1
        entry_create = ExerciseEntryCreate(exercise_id=999, workout_session_id=session_id, order=0)
        session = {"id": 1, "user_id": current_user_dict["id"]}

        with (
            patch("src.app.api.v1.workout_sessions.crud_workout_session") as mock_crud_w,
            patch("src.app.api.v1.workout_sessions.crud_exercises") as mock_crud_ex,
        ):
            mock_crud_w.get = AsyncMock(return_value=session)
            mock_crud_ex.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Exercise not found"):
                await add_exercise_to_session(Mock(), session_id, entry_create, mock_db, current_user_dict)


class TestGetExerciseEntries:
    """Test exercise entries list endpoint."""

    @pytest.mark.asyncio
    async def test_get_exercise_entries_success(self, mock_db, current_user_dict):
        """Test successful exercise entries list retrieval."""
        session_id = 1
        session = {"id": 1, "user_id": current_user_dict["id"]}
        mock_data = {"data": [{"id": 1, "workout_session_id": session_id}], "count": 1}

        with (
            patch("src.app.api.v1.workout_sessions.crud_workout_session") as mock_crud_w,
            patch("src.app.api.v1.workout_sessions.crud_exercise_entry") as mock_crud_ei,
            patch("src.app.api.v1.workout_sessions.paginated_response") as mock_paginated,
        ):
            mock_crud_w.get = AsyncMock(return_value=session)
            mock_crud_ei.get_multi = AsyncMock(return_value=mock_data)
            expected_response = {"data": [{"id": 1}], "pagination": {}}
            mock_paginated.return_value = expected_response

            result = await get_exercise_entries(
                Mock(), session_id, mock_db, current_user_dict, page=1, items_per_page=50
            )

            assert result == expected_response


class TestAddSetToEntry:
    """Test set entry creation endpoint."""

    @pytest.mark.asyncio
    async def test_add_set_to_entry_success(self, mock_db, current_user_dict):
        """Test successful set entry creation."""
        entry_id = 1
        set_create = SetEntryCreate(set_number=1, weight_kg=100.0, reps=10, exercise_entry_id=entry_id)
        entry = Mock(id=entry_id, workout_session_id=1)
        entry.workout_session_id = 1
        session = {"id": 1, "user_id": current_user_dict["id"]}
        created_mock = Mock(id=1)
        set_read = SetEntryRead(
            id=1,
            exercise_entry_id=entry_id,
            set_number=1,
            weight_kg=100.0,
            reps=10,
            created_at=datetime.now(UTC),
        )

        with (
            patch("src.app.api.v1.workout_sessions.crud_exercise_entry") as mock_crud_ei,
            patch("src.app.api.v1.workout_sessions.crud_workout_session") as mock_crud_w,
            patch("src.app.api.v1.workout_sessions.crud_set_entry") as mock_crud_s,
        ):
            mock_crud_ei.get = AsyncMock(return_value=entry)
            mock_crud_w.get = AsyncMock(return_value=session)
            mock_crud_s.create = AsyncMock(return_value=created_mock)
            mock_crud_s.get = AsyncMock(return_value=set_read)

            result = await add_set_to_entry(Mock(), entry_id, set_create, mock_db, current_user_dict)

            assert result.id == 1
            assert result.weight_kg == 100.0

    @pytest.mark.asyncio
    async def test_add_set_to_entry_exercise_entry_not_found(self, mock_db, current_user_dict):
        """Test set entry creation when exercise entry not found."""
        entry_id = 999
        set_create = SetEntryCreate(set_number=1, weight_kg=100.0, reps=10, exercise_entry_id=entry_id)

        with patch("src.app.api.v1.workout_sessions.crud_exercise_entry") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Exercise entry not found"):
                await add_set_to_entry(Mock(), entry_id, set_create, mock_db, current_user_dict)


class TestGetSetsForEntry:
    """Test sets list endpoint."""

    @pytest.mark.asyncio
    async def test_get_sets_for_entry_success(self, mock_db, current_user_dict):
        """Test successful sets list retrieval."""
        from unittest.mock import MagicMock

        entry_id = 1
        entry = Mock(id=entry_id, workout_session_id=1)
        entry.workout_session_id = 1
        session = {"id": 1, "user_id": current_user_dict["id"]}

        # Mock set entry object
        mock_set = MagicMock()
        mock_set.id = 1
        mock_set.exercise_entry_id = entry_id
        mock_set.set_number = 1
        mock_set.weight_kg = 100.0
        mock_set.reps = 10
        mock_set.rir = None
        mock_set.rpe = None
        mock_set.percentage_of_1rm = None
        mock_set.rest_seconds = None
        mock_set.tempo = None
        mock_set.notes = None
        mock_set.is_warmup = False
        mock_set.created_at = datetime.now(UTC)

        # Mock result object
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_set]

        # Mock count result
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        with (
            patch("src.app.api.v1.workout_sessions.crud_exercise_entry") as mock_crud_ei,
            patch("src.app.api.v1.workout_sessions.crud_workout_session") as mock_crud_w,
        ):
            mock_crud_ei.get = AsyncMock(return_value=entry)
            mock_crud_w.get = AsyncMock(return_value=session)
            # Mock db.execute to return different values for query and count
            mock_db.execute = AsyncMock(side_effect=[mock_result, mock_count_result])

            result = await get_sets_for_entry(Mock(), entry_id, mock_db, current_user_dict, page=1, items_per_page=50)

            assert result is not None
            assert "data" in result
            # paginated_response returns total_count, has_more, page, items_per_page, not "pagination"
            assert "total_count" in result or "pagination" in result
