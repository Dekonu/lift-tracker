"""Unit tests for workout API endpoints."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.app.api.v1.workouts import (
    create_exercise_instance,
    create_set,
    create_workout,
    delete_exercise_instance,
    delete_set,
    delete_workout,
    read_workout,
    read_workouts,
    update_set,
    update_workout,
)
from src.app.core.exceptions.http_exceptions import ForbiddenException, NotFoundException
from src.app.models.set import WeightType, WeightUnit
from src.app.schemas.exercise_instance import ExerciseInstanceCreate, ExerciseInstanceRead
from src.app.schemas.set import SetCreate, SetRead, SetUpdate
from src.app.schemas.workout import WorkoutCreate, WorkoutRead, WorkoutUpdate


class TestCreateWorkout:
    """Test workout creation endpoint."""

    @pytest.mark.asyncio
    async def test_create_workout_success(self, mock_db, current_user_dict):
        """Test successful workout creation."""
        workout_create = WorkoutCreate(date=datetime.now())
        created_mock = Mock(id=1)
        workout_read = WorkoutRead(
            id=1,
            user_id=current_user_dict["id"],
            date=datetime.now(),
            created_at=datetime.now(),
            updated_at=None,
            exercise_instances=[],
        )

        with patch("src.app.api.v1.workouts.crud_workouts") as mock_crud, patch(
            "src.app.api.v1.workouts.get_workout_with_relations"
        ) as mock_get:
            mock_crud.create = AsyncMock(return_value=created_mock)
            mock_get.return_value = workout_read

            result = await create_workout(Mock(), workout_create, mock_db, current_user_dict)

            assert result.id == 1
            assert result.user_id == current_user_dict["id"]
            mock_crud.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_workout_not_found_after_creation(self, mock_db, current_user_dict):
        """Test workout creation when workout not found after creation."""
        workout_create = WorkoutCreate(date=datetime.now())
        created_mock = Mock(id=1)

        with patch("src.app.api.v1.workouts.crud_workouts") as mock_crud, patch(
            "src.app.api.v1.workouts.get_workout_with_relations"
        ) as mock_get:
            mock_crud.create = AsyncMock(return_value=created_mock)
            mock_get.return_value = None

            with pytest.raises(NotFoundException, match="Created workout not found"):
                await create_workout(Mock(), workout_create, mock_db, current_user_dict)


class TestReadWorkout:
    """Test workout retrieval endpoint."""

    @pytest.mark.asyncio
    async def test_read_workout_success(self, mock_db, current_user_dict):
        """Test successful workout retrieval."""
        workout_id = 1
        workout_read = WorkoutRead(
            id=workout_id,
            user_id=current_user_dict["id"],
            date=datetime.now(),
            created_at=datetime.now(),
            updated_at=None,
            exercise_instances=[],
        )

        with patch("src.app.api.v1.workouts.get_workout_with_relations") as mock_get:
            mock_get.return_value = workout_read

            result = await read_workout(Mock(), workout_id, mock_db, current_user_dict)

            assert result == workout_read
            mock_get.assert_called_once_with(db=mock_db, workout_id=workout_id, user_id=current_user_dict["id"])

    @pytest.mark.asyncio
    async def test_read_workout_not_found(self, mock_db, current_user_dict):
        """Test workout retrieval when not found."""
        workout_id = 999

        with patch("src.app.api.v1.workouts.get_workout_with_relations") as mock_get:
            mock_get.return_value = None

            with pytest.raises(NotFoundException, match="Workout not found"):
                await read_workout(Mock(), workout_id, mock_db, current_user_dict)


class TestReadWorkouts:
    """Test workouts list endpoint."""

    @pytest.mark.asyncio
    async def test_read_workouts_success(self, mock_db, current_user_dict):
        """Test successful workouts list retrieval."""
        mock_data = {"data": [{"id": 1, "user_id": current_user_dict["id"]}], "count": 1}
        workout_read = WorkoutRead(
            id=1,
            user_id=current_user_dict["id"],
            date=datetime.now(),
            created_at=datetime.now(),
            updated_at=None,
            exercise_instances=[],
        )

        with patch("src.app.api.v1.workouts.crud_workouts") as mock_crud, patch(
            "src.app.api.v1.workouts.get_workout_with_relations"
        ) as mock_get, patch("src.app.api.v1.workouts.paginated_response") as mock_paginated:
            mock_crud.get_multi = AsyncMock(return_value=mock_data)
            mock_get.return_value = workout_read
            expected_response = {"data": [{"id": 1}], "pagination": {}}
            mock_paginated.return_value = expected_response

            result = await read_workouts(Mock(), mock_db, current_user_dict, page=1, items_per_page=20)

            assert result == expected_response
            mock_crud.get_multi.assert_called_once()


class TestUpdateWorkout:
    """Test workout update endpoint."""

    @pytest.mark.asyncio
    async def test_update_workout_success(self, mock_db, current_user_dict):
        """Test successful workout update."""
        workout_id = 1
        workout_update = WorkoutUpdate(date=datetime.now())
        existing = {"id": 1, "user_id": current_user_dict["id"]}

        with patch("src.app.api.v1.workouts.crud_workouts") as mock_crud:
            mock_crud.get = AsyncMock(return_value=existing)
            mock_crud.update = AsyncMock(return_value=None)

            result = await update_workout(Mock(), workout_id, workout_update, mock_db, current_user_dict)

            assert result == {"message": "Workout updated"}
            mock_crud.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_workout_not_found(self, mock_db, current_user_dict):
        """Test workout update when not found."""
        workout_id = 999
        workout_update = WorkoutUpdate(date=datetime.now())

        with patch("src.app.api.v1.workouts.crud_workouts") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Workout not found"):
                await update_workout(Mock(), workout_id, workout_update, mock_db, current_user_dict)

    @pytest.mark.asyncio
    async def test_update_workout_forbidden(self, mock_db, current_user_dict):
        """Test workout update when user doesn't own workout."""
        workout_id = 1
        workout_update = WorkoutUpdate(date=datetime.now())
        existing = {"id": 1, "user_id": 999}  # Different user

        with patch("src.app.api.v1.workouts.crud_workouts") as mock_crud:
            mock_crud.get = AsyncMock(return_value=existing)

            with pytest.raises(ForbiddenException, match="You do not have permission to update this workout"):
                await update_workout(Mock(), workout_id, workout_update, mock_db, current_user_dict)


class TestDeleteWorkout:
    """Test workout deletion endpoint."""

    @pytest.mark.asyncio
    async def test_delete_workout_success(self, mock_db, current_user_dict):
        """Test successful workout deletion."""
        workout_id = 1
        existing = {"id": 1, "user_id": current_user_dict["id"]}

        with patch("src.app.api.v1.workouts.crud_workouts") as mock_crud:
            mock_crud.get = AsyncMock(return_value=existing)
            mock_crud.db_delete = AsyncMock(return_value=None)

            result = await delete_workout(Mock(), workout_id, mock_db, current_user_dict)

            assert result == {"message": "Workout deleted"}
            mock_crud.db_delete.assert_called_once_with(db=mock_db, id=workout_id)

    @pytest.mark.asyncio
    async def test_delete_workout_forbidden(self, mock_db, current_user_dict):
        """Test workout deletion when user doesn't own workout."""
        workout_id = 1
        existing = {"id": 1, "user_id": 999}  # Different user

        with patch("src.app.api.v1.workouts.crud_workouts") as mock_crud:
            mock_crud.get = AsyncMock(return_value=existing)

            with pytest.raises(ForbiddenException, match="You do not have permission to delete this workout"):
                await delete_workout(Mock(), workout_id, mock_db, current_user_dict)


class TestCreateExerciseInstance:
    """Test exercise instance creation endpoint."""

    @pytest.mark.asyncio
    async def test_create_exercise_instance_success(self, mock_db, current_user_dict):
        """Test successful exercise instance creation."""
        workout_id = 1
        exercise_instance_create = ExerciseInstanceCreate(exercise_id=1, order=0)
        workout = {"id": 1, "user_id": current_user_dict["id"]}
        exercise = {"id": 1, "name": "Bench Press"}
        created_mock = Mock(id=1)
        exercise_instance_read = ExerciseInstanceRead(id=1, workout_id=workout_id, exercise_id=1, order=0, sets=[])

        with patch("src.app.api.v1.workouts.crud_workouts") as mock_crud_w, patch(
            "src.app.api.v1.workouts.crud_exercises"
        ) as mock_crud_ex, patch("src.app.api.v1.workouts.crud_exercise_instances") as mock_crud_ei:
            mock_crud_w.get = AsyncMock(return_value=workout)
            mock_crud_ex.get = AsyncMock(return_value=exercise)
            mock_crud_ei.create = AsyncMock(return_value=created_mock)
            mock_crud_ei.get = AsyncMock(return_value=exercise_instance_read)

            result = await create_exercise_instance(
                Mock(), workout_id, exercise_instance_create, mock_db, current_user_dict
            )

            assert result.id == 1
            assert result.workout_id == workout_id

    @pytest.mark.asyncio
    async def test_create_exercise_instance_workout_not_found(self, mock_db, current_user_dict):
        """Test exercise instance creation when workout not found."""
        workout_id = 999
        exercise_instance_create = ExerciseInstanceCreate(exercise_id=1, order=0)

        with patch("src.app.api.v1.workouts.crud_workouts") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Workout not found"):
                await create_exercise_instance(
                    Mock(), workout_id, exercise_instance_create, mock_db, current_user_dict
                )

    @pytest.mark.asyncio
    async def test_create_exercise_instance_forbidden(self, mock_db, current_user_dict):
        """Test exercise instance creation when user doesn't own workout."""
        workout_id = 1
        exercise_instance_create = ExerciseInstanceCreate(exercise_id=1, order=0)
        workout = {"id": 1, "user_id": 999}  # Different user

        with patch("src.app.api.v1.workouts.crud_workouts") as mock_crud:
            mock_crud.get = AsyncMock(return_value=workout)

            with pytest.raises(ForbiddenException, match="You do not have permission to modify this workout"):
                await create_exercise_instance(
                    Mock(), workout_id, exercise_instance_create, mock_db, current_user_dict
                )


class TestCreateSet:
    """Test set creation endpoint."""

    @pytest.mark.asyncio
    async def test_create_set_success(self, mock_db, current_user_dict):
        """Test successful set creation."""
        exercise_instance_id = 1
        set_create = SetCreate(
            weight_value=135.5,
            weight_type=WeightType.STATIC,
            unit=WeightUnit.POUNDS,
            rest_time_seconds=90,
            rir=2,
            notes="Felt strong",
        )
        exercise_instance = {"id": 1, "workout_id": 1}
        workout = {"id": 1, "user_id": current_user_dict["id"]}
        created_mock = Mock(id=1)
        set_read = SetRead(
            id=1,
            exercise_instance_id=exercise_instance_id,
            weight_value=135.5,
            weight_type=WeightType.STATIC,
            unit=WeightUnit.POUNDS,
            rest_time_seconds=90,
            rir=2,
            notes="Felt strong",
        )

        with patch("src.app.api.v1.workouts.crud_exercise_instances") as mock_crud_ei, patch(
            "src.app.api.v1.workouts.crud_workouts"
        ) as mock_crud_w, patch("src.app.api.v1.workouts.crud_sets") as mock_crud_s:
            mock_crud_ei.get = AsyncMock(return_value=exercise_instance)
            mock_crud_w.get = AsyncMock(return_value=workout)
            mock_crud_s.create = AsyncMock(return_value=created_mock)
            mock_crud_s.get = AsyncMock(return_value=set_read)

            result = await create_set(Mock(), exercise_instance_id, set_create, mock_db, current_user_dict)

            assert result.id == 1
            assert result.weight_value == 135.5

    @pytest.mark.asyncio
    async def test_create_set_exercise_instance_not_found(self, mock_db, current_user_dict):
        """Test set creation when exercise instance not found."""
        exercise_instance_id = 999
        set_create = SetCreate(
            weight_value=135.5, weight_type=WeightType.STATIC, unit=WeightUnit.POUNDS
        )

        with patch("src.app.api.v1.workouts.crud_exercise_instances") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Exercise instance not found"):
                await create_set(Mock(), exercise_instance_id, set_create, mock_db, current_user_dict)


class TestUpdateSet:
    """Test set update endpoint."""

    @pytest.mark.asyncio
    async def test_update_set_success(self, mock_db, current_user_dict):
        """Test successful set update."""
        set_id = 1
        set_update = SetUpdate(weight_value=140.0)
        set_obj = {"id": 1, "exercise_instance_id": 1}
        exercise_instance = {"id": 1, "workout_id": 1}
        workout = {"id": 1, "user_id": current_user_dict["id"]}

        with patch("src.app.api.v1.workouts.crud_sets") as mock_crud_s, patch(
            "src.app.api.v1.workouts.crud_exercise_instances"
        ) as mock_crud_ei, patch("src.app.api.v1.workouts.crud_workouts") as mock_crud_w:
            mock_crud_s.get = AsyncMock(return_value=set_obj)
            mock_crud_ei.get = AsyncMock(return_value=exercise_instance)
            mock_crud_w.get = AsyncMock(return_value=workout)
            mock_crud_s.update = AsyncMock(return_value=None)

            result = await update_set(Mock(), set_id, set_update, mock_db, current_user_dict)

            assert result == {"message": "Set updated"}
            mock_crud_s.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_set_not_found(self, mock_db, current_user_dict):
        """Test set update when set not found."""
        set_id = 999
        set_update = SetUpdate(weight_value=140.0)

        with patch("src.app.api.v1.workouts.crud_sets") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Set not found"):
                await update_set(Mock(), set_id, set_update, mock_db, current_user_dict)


class TestDeleteSet:
    """Test set deletion endpoint."""

    @pytest.mark.asyncio
    async def test_delete_set_success(self, mock_db, current_user_dict):
        """Test successful set deletion."""
        set_id = 1
        set_obj = {"id": 1, "exercise_instance_id": 1}
        exercise_instance = {"id": 1, "workout_id": 1}
        workout = {"id": 1, "user_id": current_user_dict["id"]}

        with patch("src.app.api.v1.workouts.crud_sets") as mock_crud_s, patch(
            "src.app.api.v1.workouts.crud_exercise_instances"
        ) as mock_crud_ei, patch("src.app.api.v1.workouts.crud_workouts") as mock_crud_w:
            mock_crud_s.get = AsyncMock(return_value=set_obj)
            mock_crud_ei.get = AsyncMock(return_value=exercise_instance)
            mock_crud_w.get = AsyncMock(return_value=workout)
            mock_crud_s.db_delete = AsyncMock(return_value=None)

            result = await delete_set(Mock(), set_id, mock_db, current_user_dict)

            assert result == {"message": "Set deleted"}
            mock_crud_s.db_delete.assert_called_once_with(db=mock_db, id=set_id)

