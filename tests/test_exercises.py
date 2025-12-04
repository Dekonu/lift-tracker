"""Unit tests for exercise API endpoints."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.app.api.v1.exercises import (
    create_exercise,
    delete_exercise,
    read_exercise,
    read_exercises,
    update_exercise,
)
from src.app.core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from src.app.schemas.exercise import ExerciseCreate, ExerciseRead, ExerciseUpdate


class TestCreateExercise:
    """Test exercise creation endpoint."""

    @pytest.mark.asyncio
    async def test_create_exercise_success(self, mock_db, current_user_dict):
        """Test successful exercise creation."""
        exercise_create = ExerciseCreate(
            name="Bench Press", primary_muscle_group_ids=[1], secondary_muscle_group_ids=[2, 3], equipment_ids=[]
        )
        primary_mg = {"id": 1, "name": "Chest"}
        secondary_mg1 = {"id": 2, "name": "Shoulders"}
        secondary_mg2 = {"id": 3, "name": "Triceps"}

        with (
            patch("src.app.api.v1.exercises.crud_exercises") as mock_crud_ex,
            patch("src.app.api.v1.exercises.crud_muscle_groups") as mock_crud_mg,
            patch("src.app.api.v1.exercises.create_exercise_with_muscle_groups") as mock_create,
            patch("src.app.api.v1.exercises.crud_exercise_equipment") as mock_crud_eq,
        ):
            mock_crud_ex.exists = AsyncMock(return_value=False)
            mock_crud_mg.get = AsyncMock(side_effect=[primary_mg, secondary_mg1, secondary_mg2])
            mock_create.return_value = ExerciseRead(
                id=1,
                name="Bench Press",
                primary_muscle_group_ids=[1],
                secondary_muscle_group_ids=[2, 3],
                equipment_ids=[],
            )
            mock_crud_ex.get = AsyncMock(
                return_value={
                    "id": 1,
                    "name": "Bench Press",
                    "primary_muscle_group_ids": [1],
                    "secondary_muscle_group_ids": [2, 3],
                    "equipment_ids": [],
                }
            )
            mock_crud_eq.get_by_exercise = AsyncMock(return_value=[])
            mock_crud_eq.set_equipment_for_exercise = AsyncMock()

            result = await create_exercise(Mock(), exercise_create, mock_db, current_user_dict)

            assert result.name == "Bench Press"
            assert result.id == 1
            mock_crud_ex.exists.assert_called_once_with(db=mock_db, name="Bench Press")

    @pytest.mark.asyncio
    async def test_create_exercise_duplicate_name(self, mock_db, current_user_dict):
        """Test exercise creation with duplicate name."""
        exercise_create = ExerciseCreate(
            name="Bench Press", primary_muscle_group_ids=[1], secondary_muscle_group_ids=[], equipment_ids=[]
        )

        with patch("src.app.api.v1.exercises.crud_exercises") as mock_crud:
            mock_crud.exists = AsyncMock(return_value=True)

            with pytest.raises(DuplicateValueException, match="Exercise with name"):
                await create_exercise(Mock(), exercise_create, mock_db, current_user_dict)

    @pytest.mark.asyncio
    async def test_create_exercise_invalid_primary_muscle_group(self, mock_db, current_user_dict):
        """Test exercise creation with invalid primary muscle group."""
        exercise_create = ExerciseCreate(
            name="Bench Press", primary_muscle_group_ids=[999], secondary_muscle_group_ids=[], equipment_ids=[]
        )

        with (
            patch("src.app.api.v1.exercises.crud_exercises") as mock_crud_ex,
            patch("src.app.api.v1.exercises.crud_muscle_groups") as mock_crud_mg,
        ):
            mock_crud_ex.exists = AsyncMock(return_value=False)
            mock_crud_mg.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Primary muscle group with ID"):
                await create_exercise(Mock(), exercise_create, mock_db, current_user_dict)

    @pytest.mark.asyncio
    async def test_create_exercise_invalid_secondary_muscle_group(self, mock_db, current_user_dict):
        """Test exercise creation with invalid secondary muscle group."""
        exercise_create = ExerciseCreate(
            name="Bench Press", primary_muscle_group_ids=[1], secondary_muscle_group_ids=[999], equipment_ids=[]
        )
        primary_mg = {"id": 1, "name": "Chest"}

        with (
            patch("src.app.api.v1.exercises.crud_exercises") as mock_crud_ex,
            patch("src.app.api.v1.exercises.crud_muscle_groups") as mock_crud_mg,
        ):
            mock_crud_ex.exists = AsyncMock(return_value=False)
            mock_crud_mg.get = AsyncMock(side_effect=[primary_mg, None])

            with pytest.raises(NotFoundException, match="Secondary muscle group with ID 999 not found"):
                await create_exercise(Mock(), exercise_create, mock_db, current_user_dict)


class TestReadExercise:
    """Test exercise retrieval endpoint."""

    @pytest.mark.asyncio
    async def test_read_exercise_success(self, mock_db):
        """Test successful exercise retrieval."""
        from unittest.mock import MagicMock

        exercise_id = 1
        exercise_read = ExerciseRead(
            id=exercise_id,
            name="Bench Press",
            primary_muscle_group_ids=[1],
            secondary_muscle_group_ids=[2, 3],
            equipment_ids=[],
        )

        # Mock equipment query result
        mock_equipment_result = MagicMock()
        mock_equipment_result.scalars.return_value.all.return_value = []

        # Mock muscle group query result
        mock_mg_result = MagicMock()
        mock_mg_result.scalars.return_value.all.return_value = []

        # Mock equipment names query result
        mock_eq_names_result = MagicMock()
        mock_eq_names_result.scalars.return_value.all.return_value = []

        with patch("src.app.api.v1.exercises.get_exercise_with_muscle_groups") as mock_get:
            mock_get.return_value = exercise_read
            # Mock db.execute to return different results for different queries
            mock_db.execute = AsyncMock(side_effect=[mock_equipment_result, mock_mg_result, mock_eq_names_result])

            result = await read_exercise(Mock(), exercise_id, mock_db)

            assert result.id == exercise_read.id
            assert result.name == exercise_read.name
            mock_get.assert_called_once_with(db=mock_db, exercise_id=exercise_id)

    @pytest.mark.asyncio
    async def test_read_exercise_not_found(self, mock_db):
        """Test exercise retrieval when not found."""
        exercise_id = 999

        with patch("src.app.api.v1.exercises.get_exercise_with_muscle_groups") as mock_get:
            mock_get.return_value = None

            with pytest.raises(NotFoundException, match="Exercise not found"):
                await read_exercise(Mock(), exercise_id, mock_db)


class TestReadExercises:
    """Test exercises list endpoint."""

    @pytest.mark.asyncio
    async def test_read_exercises_success(self, mock_db):
        """Test successful exercises list retrieval."""
        from unittest.mock import MagicMock

        mock_data = {
            "data": [
                {
                    "id": 1,
                    "name": "Bench Press",
                    "primary_muscle_group_ids": [1],
                    "secondary_muscle_group_ids": [],
                    "equipment_ids": [],
                    "enabled": True,
                }
            ],
            "total_count": 1,
        }

        # Mock equipment query result
        mock_equipment_result = MagicMock()
        mock_equipment_result.scalars.return_value.all.return_value = []

        # Mock muscle group query result
        mock_mg_result = MagicMock()
        mock_mg_result.scalars.return_value.all.return_value = []

        # Mock equipment names query result
        mock_eq_names_result = MagicMock()
        mock_eq_names_result.scalars.return_value.all.return_value = []

        with patch("src.app.api.v1.exercises.crud_exercises") as mock_crud:
            mock_crud.get_multi = AsyncMock(return_value=mock_data)
            # Mock db.execute for equipment queries
            mock_db.execute = AsyncMock(side_effect=[mock_equipment_result, mock_mg_result, mock_eq_names_result])

            result = await read_exercises(Mock(), mock_db, page=1, items_per_page=50)

            assert result is not None
            assert "data" in result
            mock_crud.get_multi.assert_called_once()


class TestUpdateExercise:
    """Test exercise update endpoint."""

    @pytest.mark.asyncio
    async def test_update_exercise_success(self, mock_db, current_user_dict):
        """Test successful exercise update."""
        exercise_id = 1
        exercise_update = ExerciseUpdate(name="Updated Bench Press")
        existing = {"id": 1, "name": "Bench Press"}

        with (
            patch("src.app.api.v1.exercises.crud_exercises") as mock_crud_ex,
            patch("src.app.api.v1.exercises.update_exercise_with_muscle_groups") as mock_update,
        ):
            mock_crud_ex.get = AsyncMock(return_value=existing)
            mock_crud_ex.exists = AsyncMock(return_value=False)
            mock_update.return_value = None

            result = await update_exercise(Mock(), exercise_id, exercise_update, mock_db, current_user_dict)

            assert result == {"message": "Exercise updated"}
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_exercise_not_found(self, mock_db, current_user_dict):
        """Test exercise update when not found."""
        exercise_id = 999
        exercise_update = ExerciseUpdate(name="Updated Bench Press")

        with patch("src.app.api.v1.exercises.crud_exercises") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Exercise not found"):
                await update_exercise(Mock(), exercise_id, exercise_update, mock_db, current_user_dict)

    @pytest.mark.asyncio
    async def test_update_exercise_duplicate_name(self, mock_db, current_user_dict):
        """Test exercise update with duplicate name."""
        exercise_id = 1
        exercise_update = ExerciseUpdate(name="Existing Exercise")
        existing = {"id": 1, "name": "Bench Press"}
        existing_with_name = {"id": 2, "name": "Existing Exercise"}

        with patch("src.app.api.v1.exercises.crud_exercises") as mock_crud:
            mock_crud.get = AsyncMock(side_effect=[existing, existing_with_name])
            mock_crud.exists = AsyncMock(return_value=True)

            with pytest.raises(DuplicateValueException, match="Exercise with name"):
                await update_exercise(Mock(), exercise_id, exercise_update, mock_db, current_user_dict)


class TestDeleteExercise:
    """Test exercise deletion endpoint."""

    @pytest.mark.asyncio
    async def test_delete_exercise_success(self, mock_db, current_user_dict):
        """Test successful exercise deletion."""
        exercise_id = 1
        existing = {"id": 1, "name": "Bench Press"}

        with patch("src.app.api.v1.exercises.crud_exercises") as mock_crud:
            mock_crud.get = AsyncMock(return_value=existing)
            mock_crud.db_delete = AsyncMock(return_value=None)

            result = await delete_exercise(Mock(), exercise_id, mock_db, current_user_dict)

            assert result == {"message": "Exercise deleted"}
            mock_crud.db_delete.assert_called_once_with(db=mock_db, id=exercise_id)

    @pytest.mark.asyncio
    async def test_delete_exercise_not_found(self, mock_db, current_user_dict):
        """Test exercise deletion when not found."""
        exercise_id = 999

        with patch("src.app.api.v1.exercises.crud_exercises") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Exercise not found"):
                await delete_exercise(Mock(), exercise_id, mock_db, current_user_dict)
