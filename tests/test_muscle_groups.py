"""Unit tests for muscle group API endpoints."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.app.api.v1.muscle_groups import (
    create_muscle_group,
    delete_muscle_group,
    read_muscle_group,
    read_muscle_groups,
    update_muscle_group,
)
from src.app.core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from src.app.schemas.muscle_group import MuscleGroupCreate, MuscleGroupRead, MuscleGroupUpdate


class TestCreateMuscleGroup:
    """Test muscle group creation endpoint."""

    @pytest.mark.asyncio
    async def test_create_muscle_group_success(self, mock_db, current_user_dict):
        """Test successful muscle group creation."""
        muscle_group_create = MuscleGroupCreate(name="Chest")
        created_mock = Mock(id=1)

        with patch("src.app.api.v1.muscle_groups.crud_muscle_groups") as mock_crud:
            mock_crud.exists = AsyncMock(return_value=False)
            mock_crud.create = AsyncMock(return_value=created_mock)
            mock_crud.get = AsyncMock(return_value=MuscleGroupRead(id=1, name="Chest"))

            result = await create_muscle_group(Mock(), muscle_group_create, mock_db, current_user_dict)

            assert result.name == "Chest"
            assert result.id == 1
            mock_crud.exists.assert_called_once_with(db=mock_db, name="Chest")
            mock_crud.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_muscle_group_duplicate_name(self, mock_db, current_user_dict):
        """Test muscle group creation with duplicate name."""
        muscle_group_create = MuscleGroupCreate(name="Chest")

        with patch("src.app.api.v1.muscle_groups.crud_muscle_groups") as mock_crud:
            mock_crud.exists = AsyncMock(return_value=True)

            with pytest.raises(DuplicateValueException, match="Muscle group with this name already exists"):
                await create_muscle_group(Mock(), muscle_group_create, mock_db, current_user_dict)


class TestReadMuscleGroup:
    """Test muscle group retrieval endpoint."""

    @pytest.mark.asyncio
    async def test_read_muscle_group_success(self, mock_db):
        """Test successful muscle group retrieval."""
        muscle_group_id = 1
        muscle_group_read = MuscleGroupRead(id=muscle_group_id, name="Chest")

        with patch("src.app.api.v1.muscle_groups.crud_muscle_groups") as mock_crud:
            mock_crud.get = AsyncMock(return_value=muscle_group_read)

            result = await read_muscle_group(Mock(), muscle_group_id, mock_db)

            assert result == muscle_group_read
            mock_crud.get.assert_called_once_with(db=mock_db, id=muscle_group_id, schema_to_select=MuscleGroupRead)

    @pytest.mark.asyncio
    async def test_read_muscle_group_not_found(self, mock_db):
        """Test muscle group retrieval when not found."""
        muscle_group_id = 999

        with patch("src.app.api.v1.muscle_groups.crud_muscle_groups") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Muscle group not found"):
                await read_muscle_group(Mock(), muscle_group_id, mock_db)


class TestReadMuscleGroups:
    """Test muscle groups list endpoint."""

    @pytest.mark.asyncio
    async def test_read_muscle_groups_success(self, mock_db):
        """Test successful muscle groups list retrieval."""
        mock_data = {"data": [{"id": 1}, {"id": 2}], "count": 2}

        with patch("src.app.api.v1.muscle_groups.crud_muscle_groups") as mock_crud:
            mock_crud.get_multi = AsyncMock(return_value=mock_data)

            with patch("src.app.api.v1.muscle_groups.paginated_response") as mock_paginated:
                expected_response = {"data": [{"id": 1}, {"id": 2}], "pagination": {}}
                mock_paginated.return_value = expected_response

                result = await read_muscle_groups(Mock(), mock_db, page=1, items_per_page=50)

                assert result == expected_response
                mock_crud.get_multi.assert_called_once()
                mock_paginated.assert_called_once()


class TestUpdateMuscleGroup:
    """Test muscle group update endpoint."""

    @pytest.mark.asyncio
    async def test_update_muscle_group_success(self, mock_db, current_user_dict):
        """Test successful muscle group update."""
        muscle_group_id = 1
        muscle_group_update = MuscleGroupUpdate(name="Updated Chest")
        existing = {"id": 1, "name": "Chest"}

        with patch("src.app.api.v1.muscle_groups.crud_muscle_groups") as mock_crud:
            mock_crud.get = AsyncMock(return_value=existing)
            mock_crud.exists = AsyncMock(return_value=False)
            mock_crud.update = AsyncMock(return_value=None)

            result = await update_muscle_group(Mock(), muscle_group_id, muscle_group_update, mock_db, current_user_dict)

            assert result == {"message": "Muscle group updated"}
            mock_crud.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_muscle_group_not_found(self, mock_db, current_user_dict):
        """Test muscle group update when not found."""
        muscle_group_id = 999
        muscle_group_update = MuscleGroupUpdate(name="Updated Chest")

        with patch("src.app.api.v1.muscle_groups.crud_muscle_groups") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Muscle group not found"):
                await update_muscle_group(Mock(), muscle_group_id, muscle_group_update, mock_db, current_user_dict)

    @pytest.mark.asyncio
    async def test_update_muscle_group_duplicate_name(self, mock_db, current_user_dict):
        """Test muscle group update with duplicate name."""
        muscle_group_id = 1
        muscle_group_update = MuscleGroupUpdate(name="Existing Name")
        existing = {"id": 1, "name": "Chest"}
        existing_with_name = {"id": 2, "name": "Existing Name"}

        with patch("src.app.api.v1.muscle_groups.crud_muscle_groups") as mock_crud:
            mock_crud.get = AsyncMock(side_effect=[existing, existing_with_name])
            mock_crud.exists = AsyncMock(return_value=True)

            with pytest.raises(DuplicateValueException, match="Muscle group with this name already exists"):
                await update_muscle_group(Mock(), muscle_group_id, muscle_group_update, mock_db, current_user_dict)


class TestDeleteMuscleGroup:
    """Test muscle group deletion endpoint."""

    @pytest.mark.asyncio
    async def test_delete_muscle_group_success(self, mock_db, current_user_dict):
        """Test successful muscle group deletion."""
        muscle_group_id = 1
        existing = {"id": 1, "name": "Chest"}

        with patch("src.app.api.v1.muscle_groups.crud_muscle_groups") as mock_crud:
            mock_crud.get = AsyncMock(return_value=existing)
            mock_crud.db_delete = AsyncMock(return_value=None)

            result = await delete_muscle_group(Mock(), muscle_group_id, mock_db, current_user_dict)

            assert result == {"message": "Muscle group deleted"}
            mock_crud.db_delete.assert_called_once_with(db=mock_db, id=muscle_group_id)

    @pytest.mark.asyncio
    async def test_delete_muscle_group_not_found(self, mock_db, current_user_dict):
        """Test muscle group deletion when not found."""
        muscle_group_id = 999

        with patch("src.app.api.v1.muscle_groups.crud_muscle_groups") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="Muscle group not found"):
                await delete_muscle_group(Mock(), muscle_group_id, mock_db, current_user_dict)
