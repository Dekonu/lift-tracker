import csv
import io
from typing import Annotated, Any, cast

import httpx
from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy import exc as sqlalchemy_exc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...api.dependencies import get_current_user, get_optional_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_exercise import (
    create_exercise_with_muscle_groups,
    crud_exercises,
    get_exercise_with_muscle_groups,
    update_exercise_with_muscle_groups,
)
from ...crud.crud_exercise_equipment import crud_exercise_equipment
from ...crud.crud_equipment import crud_equipment
from ...crud.crud_muscle_group import crud_muscle_groups
from ...schemas.exercise import ExerciseCreate, ExerciseRead, ExerciseUpdate
from ...schemas.muscle_group import MuscleGroupCreate

router = APIRouter(tags=["exercises"])


@router.post("/exercise", response_model=ExerciseRead, status_code=201)
async def create_exercise(
    request: Request,
    exercise: ExerciseCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ExerciseRead:
    """Create a new exercise."""
    # Check if exercise name already exists (case-insensitive check for safety)
    existing = await crud_exercises.exists(db=db, name=exercise.name)
    if existing:
        raise DuplicateValueException(f"Exercise with name '{exercise.name}' already exists")

    # Validate primary muscle groups exist
    if not exercise.primary_muscle_group_ids:
        raise NotFoundException("At least one primary muscle group is required")
    
    for mg_id in exercise.primary_muscle_group_ids:
        mg = await crud_muscle_groups.get(db=db, id=mg_id)
        if mg is None:
            raise NotFoundException(f"Primary muscle group with ID {mg_id} not found")

    # Validate secondary muscle groups exist
    if exercise.secondary_muscle_group_ids:
        for mg_id in exercise.secondary_muscle_group_ids:
            mg = await crud_muscle_groups.get(db=db, id=mg_id)
            if mg is None:
                raise NotFoundException(f"Secondary muscle group with ID {mg_id} not found")

    # Validate equipment exists
    if exercise.equipment_ids:
        for eq_id in exercise.equipment_ids:
            equipment = await crud_equipment.get(db=db, id=eq_id)
            if equipment is None:
                raise NotFoundException(f"Equipment with ID {eq_id} not found")

    # Extract equipment_ids before creating exercise
    equipment_ids = exercise.equipment_ids or []
    
    # Create exercise (without equipment_ids in the model)
    exercise_data_no_equipment = exercise.model_copy()
    exercise_data_no_equipment.equipment_ids = []
    created = await create_exercise_with_muscle_groups(db=db, exercise_data=exercise_data_no_equipment)
    
    # Link equipment
    created_id = created.id if hasattr(created, "id") else created["id"]
    if equipment_ids:
        await crud_exercise_equipment.set_equipment_for_exercise(db=db, exercise_id=created_id, equipment_ids=equipment_ids)
        await db.commit()
    
    # Fetch exercise with equipment
    exercise_read = await crud_exercises.get(db=db, id=created_id, schema_to_select=ExerciseRead)
    if exercise_read:
        # Get equipment IDs
        equipment_links = await crud_exercise_equipment.get_by_exercise(db=db, exercise_id=created_id)
        equipment_ids_list = [link.equipment_id if hasattr(link, "equipment_id") else link["equipment_id"] for link in equipment_links]
        
        # Add equipment_ids to response
        if isinstance(exercise_read, dict):
            exercise_read["equipment_ids"] = equipment_ids_list
        else:
            exercise_read.equipment_ids = equipment_ids_list
        
        return ExerciseRead(**exercise_read) if isinstance(exercise_read, dict) else ExerciseRead.model_validate(exercise_read)
    
    return cast(ExerciseRead, created)


@router.get("/exercises", response_model=PaginatedListResponse[ExerciseRead])
async def read_exercises(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 50,
    current_user: Annotated[dict | None, Depends(get_optional_user)] = None,
    equipment_ids: str | None = None,  # Comma-separated list of equipment IDs
) -> dict[str, Any]:
    """Get all exercises. Only returns enabled exercises for non-admin users.
    
    Can filter by equipment_ids (comma-separated). Returns exercises that require
    ALL specified equipment (AND relationship).
    """
    # Check if user is admin/superuser
    is_admin = current_user and current_user.get("is_superuser", False)
    
    # Filter by enabled status if not admin
    filters = {}
    if not is_admin:
        filters["enabled"] = True
    
    # Optimize equipment filtering with SQL JOIN
    if equipment_ids:
        from ...models.exercise import Exercise
        from ...models.exercise_equipment import ExerciseEquipment
        
        equipment_id_list = [int(eq_id.strip()) for eq_id in equipment_ids.split(",") if eq_id.strip()]
        
        # Use SQL JOIN to find exercises that have ALL required equipment
        # This is much faster than fetching all and filtering in Python
        stmt = (
            select(Exercise)
            .join(ExerciseEquipment, Exercise.id == ExerciseEquipment.exercise_id)
            .where(ExerciseEquipment.equipment_id.in_(equipment_id_list))
            .group_by(Exercise.id)
            .having(func.count(ExerciseEquipment.equipment_id.distinct()) == len(equipment_id_list))
        )
        
        # Add enabled filter if not admin
        if not is_admin:
            stmt = stmt.where(Exercise.enabled == True)
        
        result = await db.execute(stmt)
        exercise_models = result.scalars().all()
        
        # Get total count
        count_subquery = (
            select(Exercise.id)
            .join(ExerciseEquipment, Exercise.id == ExerciseEquipment.exercise_id)
            .where(ExerciseEquipment.equipment_id.in_(equipment_id_list))
            .group_by(Exercise.id)
            .having(func.count(ExerciseEquipment.equipment_id.distinct()) == len(equipment_id_list))
        )
        if not is_admin:
            count_subquery = count_subquery.where(Exercise.enabled == True)
        
        count_stmt = select(func.count()).select_from(count_subquery.subquery())
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar() or 0
        
        # Paginate
        start = compute_offset(page, items_per_page)
        paginated_exercises = exercise_models[start:start + items_per_page]
        
        # Convert to schema and fetch equipment IDs in batch
        exercise_ids = [ex.id for ex in paginated_exercises]
        if exercise_ids:
            # Batch fetch all equipment links for this page
            equipment_links_stmt = select(ExerciseEquipment).where(
                ExerciseEquipment.exercise_id.in_(exercise_ids)
            )
            equipment_result = await db.execute(equipment_links_stmt)
            all_equipment_links = equipment_result.scalars().all()
            
            # Group equipment by exercise_id
            equipment_by_exercise: dict[int, list[int]] = {}
            for link in all_equipment_links:
                if link.exercise_id not in equipment_by_exercise:
                    equipment_by_exercise[link.exercise_id] = []
                equipment_by_exercise[link.exercise_id].append(link.equipment_id)
        else:
            equipment_by_exercise = {}
        
        # Convert to ExerciseRead schema
        exercises = []
        for ex in paginated_exercises:
            ex_dict = {
                "id": ex.id,
                "name": ex.name,
                "primary_muscle_group_ids": ex.primary_muscle_group_ids or [],
                "secondary_muscle_group_ids": ex.secondary_muscle_group_ids or [],
                "enabled": ex.enabled,
                "category_id": ex.category_id,
                "instructions": ex.instructions,
                "common_mistakes": ex.common_mistakes,
                "equipment_ids": equipment_by_exercise.get(ex.id, []),
            }
            exercises.append(ExerciseRead(**ex_dict))
    else:
        # Get exercises with pagination (normal case - much faster)
        exercises_data = await crud_exercises.get_multi(
            db=db,
            offset=compute_offset(page, items_per_page),
            limit=items_per_page,
            schema_to_select=ExerciseRead,
            return_total_count=True,
            **filters,
        )
        
        exercises = exercises_data.get("data", [])
        total_count = exercises_data.get("total_count", 0)
        
        # Batch fetch equipment_ids for all exercises on this page
        if exercises:
            from ...models.exercise_equipment import ExerciseEquipment
            
            exercise_ids = [
                ex.id if hasattr(ex, "id") else ex["id"] 
                for ex in exercises
            ]
            
            # Single query to get all equipment links for this page
            equipment_links_stmt = select(ExerciseEquipment).where(
                ExerciseEquipment.exercise_id.in_(exercise_ids)
            )
            equipment_result = await db.execute(equipment_links_stmt)
            all_equipment_links = equipment_result.scalars().all()
            
            # Group equipment by exercise_id
            equipment_by_exercise: dict[int, list[int]] = {}
            for link in all_equipment_links:
                if link.exercise_id not in equipment_by_exercise:
                    equipment_by_exercise[link.exercise_id] = []
                equipment_by_exercise[link.exercise_id].append(link.equipment_id)
            
            # Add equipment_ids to exercises
            for exercise in exercises:
                exercise_id = exercise.id if hasattr(exercise, "id") else exercise["id"]
                equipment_ids_list = equipment_by_exercise.get(exercise_id, [])
                if isinstance(exercise, dict):
                    exercise["equipment_ids"] = equipment_ids_list
                else:
                    exercise.equipment_ids = equipment_ids_list
    
    # Calculate has_more
    has_more = (page * items_per_page) < total_count
    
    return {
        "data": exercises,
        "total_count": total_count,
        "has_more": has_more,
        "page": page,
        "items_per_page": items_per_page,
    }


@router.get("/exercise/{exercise_id}", response_model=ExerciseRead)
async def read_exercise(
    request: Request,
    exercise_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict | None, Depends(get_optional_user)] = None,
) -> ExerciseRead:
    """Get an exercise by ID. Only returns enabled exercises for non-admin users."""
    exercise = await get_exercise_with_muscle_groups(db=db, exercise_id=exercise_id)
    if exercise is None:
        raise NotFoundException("Exercise not found")
    
    # Check if user is admin/superuser
    is_admin = current_user and current_user.get("is_superuser", False)
    
    # Check if exercise is enabled (for non-admin users)
    if not is_admin:
        if isinstance(exercise, dict):
            enabled = exercise.get("enabled", True)
        else:
            enabled = getattr(exercise, "enabled", True)
        if not enabled:
            raise NotFoundException("Exercise not found")
    
    # Get equipment IDs
    equipment_links = await crud_exercise_equipment.get_by_exercise(db=db, exercise_id=exercise_id)
    equipment_ids_list = [
        link.equipment_id if hasattr(link, "equipment_id") else link["equipment_id"]
        for link in equipment_links
    ]
    
    # Add equipment_ids to exercise
    if isinstance(exercise, dict):
        exercise["equipment_ids"] = equipment_ids_list
    else:
        exercise.equipment_ids = equipment_ids_list

    return cast(ExerciseRead, exercise)


@router.patch("/exercise/{exercise_id}")
async def update_exercise(
    request: Request,
    exercise_id: int,
    values: ExerciseUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Update an exercise."""
    existing = await crud_exercises.get(db=db, id=exercise_id)
    if existing is None:
        raise NotFoundException("Exercise not found")

    # Check if new name conflicts
    if values.name is not None:
        name_exists = await crud_exercises.exists(db=db, name=values.name)
        if name_exists:
            existing_with_name = await crud_exercises.get(db=db, name=values.name)
            if isinstance(existing, dict):
                existing_id = existing.get("id")
            else:
                existing_id = existing.id
            if isinstance(existing_with_name, dict):
                existing_name_id = existing_with_name.get("id")
            else:
                existing_name_id = existing_with_name.id
            if existing_name_id != existing_id:
                raise DuplicateValueException(f"Exercise with name '{values.name}' already exists")

    # Validate primary muscle groups if provided
    if values.primary_muscle_group_ids is not None:
        if not values.primary_muscle_group_ids:
            raise NotFoundException("At least one primary muscle group is required")
        for mg_id in values.primary_muscle_group_ids:
            mg = await crud_muscle_groups.get(db=db, id=mg_id)
            if mg is None:
                raise NotFoundException(f"Primary muscle group with ID {mg_id} not found")

    # Validate secondary muscle groups if provided
    if values.secondary_muscle_group_ids is not None:
        for mg_id in values.secondary_muscle_group_ids:
            mg = await crud_muscle_groups.get(db=db, id=mg_id)
            if mg is None:
                raise NotFoundException(f"Secondary muscle group with ID {mg_id} not found")
    
    # Validate equipment if provided
    equipment_ids = None
    if values.equipment_ids is not None:
        equipment_ids = values.equipment_ids
        for eq_id in equipment_ids:
            equipment = await crud_equipment.get(db=db, id=eq_id)
            if equipment is None:
                raise NotFoundException(f"Equipment with ID {eq_id} not found")
    
    # Update exercise (without equipment_ids)
    exercise_data_no_equipment = values.model_copy()
    exercise_data_no_equipment.equipment_ids = None
    await update_exercise_with_muscle_groups(db=db, exercise_id=exercise_id, exercise_data=exercise_data_no_equipment)
    
    # Update equipment links if provided
    if equipment_ids is not None:
        await crud_exercise_equipment.set_equipment_for_exercise(db=db, exercise_id=exercise_id, equipment_ids=equipment_ids)
        await db.commit()
    
    return {"message": "Exercise updated"}


@router.delete("/exercise/{exercise_id}")
async def delete_exercise(
    request: Request,
    exercise_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete an exercise."""
    existing = await crud_exercises.get(db=db, id=exercise_id)
    if existing is None:
        raise NotFoundException("Exercise not found")

    await crud_exercises.db_delete(db=db, id=exercise_id)
    return {"message": "Exercise deleted"}


@router.get("/exercises/export")
async def export_exercises(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> StreamingResponse:
    """Export all exercises as CSV."""
    # Get all exercises (with a high limit to get all)
    exercises_data = await crud_exercises.get_multi(
        db=db,
        offset=0,
        limit=10000,
        schema_to_select=ExerciseRead,
    )
    exercises = exercises_data.get("data", [])
    
    # Get all muscle groups for name mapping
    muscle_groups_data = await crud_muscle_groups.get_multi(
        db=db,
        offset=0,
        limit=10000,
    )
    muscle_groups = muscle_groups_data.get("data", [])
    muscle_group_map = {mg.get("id") if isinstance(mg, dict) else mg.id: mg.get("name") if isinstance(mg, dict) else mg.name for mg in muscle_groups}
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["name", "primary_muscle_groups", "secondary_muscle_groups", "enabled"])
    
    # Write data
    for exercise in exercises:
        if isinstance(exercise, dict):
            name = exercise.get("name", "")
            primary_ids = exercise.get("primary_muscle_group_ids", [])
            secondary_ids = exercise.get("secondary_muscle_group_ids", [])
            enabled = exercise.get("enabled", True)
        else:
            name = exercise.name
            primary_ids = exercise.primary_muscle_group_ids or []
            secondary_ids = exercise.secondary_muscle_group_ids or []
            enabled = getattr(exercise, "enabled", True)
        
        primary_names = [muscle_group_map.get(pid, f"ID:{pid}") for pid in primary_ids]
        primary_str = ", ".join(primary_names) if primary_names else ""
        secondary_names = [muscle_group_map.get(sid, f"ID:{sid}") for sid in secondary_ids]
        secondary_str = ", ".join(secondary_names) if secondary_names else ""
        
        writer.writerow([name, primary_str, secondary_str, "true" if enabled else "false"])
    
    output.seek(0)
    
    # Return as downloadable CSV
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=exercises_export.csv"}
    )


@router.post("/exercises/import")
async def import_exercises(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Import exercises from CSV file with change data capture (CDC).
    
    Only exercises that are new or changed will be created/updated.
    No exercises will be deleted.
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise NotFoundException("File must be a CSV file")
    
    # Read and parse CSV
    contents = await file.read()
    csv_content = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    
    # Get all existing exercises and muscle groups
    exercises_data = await crud_exercises.get_multi(
        db=db,
        offset=0,
        limit=10000,
        schema_to_select=ExerciseRead,
    )
    existing_exercises = exercises_data.get("data", [])
    
    # Create a map of existing exercises by name (case-insensitive)
    existing_exercise_map: dict[str, ExerciseRead] = {}
    for ex in existing_exercises:
        if isinstance(ex, dict):
            name = ex.get("name", "")
        else:
            name = ex.name
        existing_exercise_map[name.lower()] = cast(ExerciseRead, ex)
    
    # Get all muscle groups
    muscle_groups_data = await crud_muscle_groups.get_multi(
        db=db,
        offset=0,
        limit=10000,
    )
    muscle_groups = muscle_groups_data.get("data", [])
    muscle_group_name_map: dict[str, int] = {}
    for mg in muscle_groups:
        if isinstance(mg, dict):
            mg_id = mg.get("id")
            mg_name = mg.get("name", "")
        else:
            mg_id = mg.id
            mg_name = mg.name
        muscle_group_name_map[mg_name.lower()] = mg_id
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    errors: list[str] = []
    
    # Process each row
    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is header
        try:
            name = row.get("name", "").strip()
            if not name:
                errors.append(f"Row {row_num}: Exercise name is required")
                continue
            
            # Parse primary muscle groups (comma-separated)
            primary_muscle_groups_str = row.get("primary_muscle_groups", "").strip()
            if not primary_muscle_groups_str:
                errors.append(f"Row {row_num}: At least one primary muscle group is required")
                continue
            
            primary_muscle_group_names = [s.strip() for s in primary_muscle_groups_str.split(",") if s.strip()]
            if not primary_muscle_group_names:
                errors.append(f"Row {row_num}: At least one primary muscle group is required")
                continue
            
            # Find primary muscle group IDs
            primary_ids: list[int] = []
            for primary_name in primary_muscle_group_names:
                primary_id = muscle_group_name_map.get(primary_name.lower())
                if primary_id is None:
                    errors.append(f"Row {row_num}: Primary muscle group '{primary_name}' not found")
                    continue
                if primary_id not in primary_ids:
                    primary_ids.append(primary_id)
            
            # Parse secondary muscle groups
            secondary_str = row.get("secondary_muscle_groups", "").strip()
            secondary_ids: list[int] = []
            if secondary_str:
                secondary_names = [s.strip() for s in secondary_str.split(",") if s.strip()]
                for sec_name in secondary_names:
                    sec_id = muscle_group_name_map.get(sec_name.lower())
                    if sec_id is None:
                        errors.append(f"Row {row_num}: Secondary muscle group '{sec_name}' not found")
                        continue
                    if sec_id not in secondary_ids:
                        secondary_ids.append(sec_id)
            
            # Parse enabled flag (defaults to true if not specified)
            enabled_str = row.get("enabled", "true").strip().lower()
            enabled = enabled_str in ("true", "1", "yes", "y")
            
            # Check if exercise exists (case-insensitive match)
            existing_exercise = existing_exercise_map.get(name.lower())
            
            if existing_exercise:
                # Exercise exists - check if it needs updating
                if isinstance(existing_exercise, dict):
                    existing_name = existing_exercise.get("name", "")
                    existing_primary = set(existing_exercise.get("primary_muscle_group_ids", []))
                    existing_secondary = set(existing_exercise.get("secondary_muscle_group_ids", []))
                    existing_enabled = existing_exercise.get("enabled", True)
                    exercise_id = existing_exercise.get("id")
                else:
                    existing_name = existing_exercise.name
                    existing_primary = set(existing_exercise.primary_muscle_group_ids or [])
                    existing_secondary = set(existing_exercise.secondary_muscle_group_ids or [])
                    existing_enabled = getattr(existing_exercise, "enabled", True)
                    exercise_id = existing_exercise.id
                
                # Check if anything changed
                needs_update = (
                    existing_name != name or
                    existing_primary != set(primary_ids) or
                    existing_secondary != set(secondary_ids) or
                    existing_enabled != enabled
                )
                
                if needs_update:
                    # Update exercise
                    update_data = ExerciseUpdate(
                        name=name if existing_name != name else None,
                        primary_muscle_group_ids=primary_ids if existing_primary != set(primary_ids) else None,
                        secondary_muscle_group_ids=secondary_ids if existing_secondary != set(secondary_ids) else None,
                        enabled=enabled if existing_enabled != enabled else None
                    )
                    await update_exercise_with_muscle_groups(
                        db=db,
                        exercise_id=exercise_id,
                        exercise_data=update_data
                    )
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                # New exercise - create it
                create_data = ExerciseCreate(
                    name=name,
                    primary_muscle_group_ids=primary_ids,
                    secondary_muscle_group_ids=secondary_ids,
                    enabled=enabled
                )
                await create_exercise_with_muscle_groups(db=db, exercise_data=create_data)
                created_count += 1
                
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            continue
    
    await db.commit()
    
    return {
        "message": "Import completed",
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "errors": errors
    }


@router.post("/exercises/sync-wger")
async def sync_exercises_from_wger(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    full_sync: bool = Query(default=False, description="If True, truncates all exercises and reloads from Wger"),
) -> dict[str, Any]:
    """Sync exercises from Wger API (https://wger.de/api/v2/).
    
    Fetches all exercises and their muscle groups from Wger API,
    creates missing muscle groups, and creates/updates exercises.
    
    Args:
        full_sync: If True, truncates all exercises and reloads from Wger.
                   If False, uses change data capture - only new or changed exercises are created/updated.
    """
    WGER_API_BASE = "https://wger.de/api/v2"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Fetch all muscles from Wger to map IDs to names
        muscles_map: dict[int, str] = {}
        muscles_url = f"{WGER_API_BASE}/muscle/"
        muscles_next = muscles_url
        
        while muscles_next:
            try:
                muscles_response = await client.get(muscles_next)
                muscles_response.raise_for_status()
                muscles_data = muscles_response.json()
                
                for muscle in muscles_data.get("results", []):
                    muscle_id = muscle.get("id")
                    muscle_name = muscle.get("name", "").strip()
                    if muscle_id and muscle_name:
                        muscles_map[muscle_id] = muscle_name
                
                muscles_next = muscles_data.get("next")
            except Exception as e:
                return {
                    "message": "Failed to fetch muscles from Wger API",
                    "error": str(e),
                    "created": 0,
                    "updated": 0,
                    "skipped": 0,
                    "muscle_groups_created": 0
                }
        
        # Get all existing muscle groups (preserved in both sync modes - only new ones are added)
        muscle_groups_data = await crud_muscle_groups.get_multi(
            db=db,
            offset=0,
            limit=10000,
        )
        existing_muscle_groups = muscle_groups_data.get("data", [])
        muscle_group_name_map: dict[str, int] = {}
        for mg in existing_muscle_groups:
            if isinstance(mg, dict):
                mg_id = mg.get("id")
                mg_name = mg.get("name", "").strip()
            else:
                mg_id = mg.id
                mg_name = mg.name.strip()
            muscle_group_name_map[mg_name.lower()] = mg_id
        
        # Handle full sync - truncate all exercises (but preserve muscle groups)
        if full_sync:
            # Delete all exercises
            exercises_data = await crud_exercises.get_multi(
                db=db,
                offset=0,
                limit=10000,
            )
            all_exercises = exercises_data.get("data", [])
            for ex in all_exercises:
                if isinstance(ex, dict):
                    ex_id = ex.get("id")
                else:
                    ex_id = ex.id
                if ex_id:
                    await crud_exercises.db_delete(db=db, id=ex_id)
            
            await db.commit()
            existing_exercise_map: dict[str, ExerciseRead] = {}
        else:
            # Get all existing exercises for CDC
            exercises_data = await crud_exercises.get_multi(
                db=db,
                offset=0,
                limit=10000,
                schema_to_select=ExerciseRead,
            )
            existing_exercises = exercises_data.get("data", [])
            existing_exercise_map: dict[str, ExerciseRead] = {}
            for ex in existing_exercises:
                if isinstance(ex, dict):
                    name = ex.get("name", "")
                else:
                    name = ex.name
                existing_exercise_map[name.lower()] = cast(ExerciseRead, ex)
        
        # Fetch all exercise translations to get names (prefer English)
        exercise_translations_map: dict[int, str] = {}
        translations_url = f"{WGER_API_BASE}/exercise-translation/?language=2"  # Language 2 is English
        translations_next = translations_url
        
        while translations_next:
            try:
                translations_response = await client.get(translations_next)
                translations_response.raise_for_status()
                translations_data = translations_response.json()
                
                for translation in translations_data.get("results", []):
                    exercise_id = translation.get("exercise")
                    exercise_name = translation.get("name", "").strip()
                    if exercise_id and exercise_name:
                        # Prefer English, but update if we find a better translation
                        if exercise_id not in exercise_translations_map:
                            exercise_translations_map[exercise_id] = exercise_name
                
                translations_next = translations_data.get("next")
            except Exception as e:
                # If English translations fail, try to get any language
                break
        
        # If no English translations, try to get any language
        if not exercise_translations_map:
            translations_url = f"{WGER_API_BASE}/exercise-translation/"
            translations_next = translations_url
            while translations_next:
                try:
                    translations_response = await client.get(translations_next)
                    translations_response.raise_for_status()
                    translations_data = translations_response.json()
                    
                    for translation in translations_data.get("results", []):
                        exercise_id = translation.get("exercise")
                        exercise_name = translation.get("name", "").strip()
                        if exercise_id and exercise_name and exercise_id not in exercise_translations_map:
                            exercise_translations_map[exercise_id] = exercise_name
                    
                    translations_next = translations_data.get("next")
                except Exception as e:
                    break
        
        # Fetch all exercises from Wger
        exercises_url = f"{WGER_API_BASE}/exercise/"
        exercises_next = exercises_url
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        muscle_groups_created = 0
        errors: list[str] = []
        
        while exercises_next:
            try:
                exercises_response = await client.get(exercises_next)
                exercises_response.raise_for_status()
                exercises_data = exercises_response.json()
                
                for wger_exercise in exercises_data.get("results", []):
                    try:
                        # Get exercise name from translations map
                        exercise_id = wger_exercise.get("id")
                        exercise_name = exercise_translations_map.get(exercise_id)
                        
                        if not exercise_name:
                            errors.append(f"Exercise ID {exercise_id}: No name found in translations")
                            continue
                        
                        # Get muscle IDs from Wger exercise
                        muscles = wger_exercise.get("muscles", [])  # Primary muscles
                        muscles_secondary = wger_exercise.get("muscles_secondary", [])  # Secondary muscles
                        
                        # Map all primary muscles to muscle group IDs
                        if not muscles:
                            errors.append(f"Exercise '{exercise_name}': No primary muscles found")
                            continue
                        
                        primary_mg_ids: list[int] = []
                        for primary_muscle_id in muscles:
                            primary_muscle_name = muscles_map.get(primary_muscle_id)
                            if not primary_muscle_name:
                                errors.append(f"Exercise '{exercise_name}': Primary muscle ID {primary_muscle_id} not found in muscles map")
                                continue
                            
                            # Get or create primary muscle group
                            primary_mg_id = muscle_group_name_map.get(primary_muscle_name.lower())
                            if primary_mg_id is None:
                                # Create new muscle group
                                try:
                                    new_mg = MuscleGroupCreate(name=primary_muscle_name)
                                    created_mg = await crud_muscle_groups.create(db=db, object=new_mg)
                                    await db.commit()
                                    await db.refresh(created_mg)
                                    primary_mg_id = created_mg.id
                                    muscle_group_name_map[primary_muscle_name.lower()] = primary_mg_id
                                    muscle_groups_created += 1
                                except Exception as e:
                                    errors.append(f"Exercise '{exercise_name}': Failed to create muscle group '{primary_muscle_name}': {str(e)}")
                                    continue
                            
                            if primary_mg_id not in primary_mg_ids:
                                primary_mg_ids.append(primary_mg_id)
                        
                        # Map secondary muscles
                        secondary_mg_ids: list[int] = []
                        for sec_muscle_id in muscles_secondary:
                            sec_muscle_name = muscles_map.get(sec_muscle_id)
                            if not sec_muscle_name:
                                continue
                            
                            sec_mg_id = muscle_group_name_map.get(sec_muscle_name.lower())
                            if sec_mg_id is None:
                                # Create new muscle group
                                try:
                                    new_mg = MuscleGroupCreate(name=sec_muscle_name)
                                    created_mg = await crud_muscle_groups.create(db=db, object=new_mg)
                                    await db.commit()
                                    await db.refresh(created_mg)
                                    sec_mg_id = created_mg.id
                                    muscle_group_name_map[sec_muscle_name.lower()] = sec_mg_id
                                    muscle_groups_created += 1
                                except Exception as e:
                                    errors.append(f"Exercise '{exercise_name}': Failed to create secondary muscle group '{sec_muscle_name}': {str(e)}")
                                    continue
                            
                            if sec_mg_id not in secondary_mg_ids:
                                secondary_mg_ids.append(sec_mg_id)
                        
                        # Check if exercise exists (case-insensitive match)
                        existing_exercise = existing_exercise_map.get(exercise_name.lower())
                        
                        # If not in map, check database directly (might have been created in this batch)
                        if not existing_exercise:
                            existing_check = await crud_exercises.get(
                                db=db,
                                name=exercise_name,
                                schema_to_select=ExerciseRead
                            )
                            if existing_check:
                                existing_exercise = cast(ExerciseRead, existing_check)
                                existing_exercise_map[exercise_name.lower()] = existing_exercise
                        
                        if existing_exercise:
                            # Exercise exists - check if it needs updating
                            if isinstance(existing_exercise, dict):
                                existing_name = existing_exercise.get("name", "")
                                existing_primary = set(existing_exercise.get("primary_muscle_group_ids", []))
                                existing_secondary = set(existing_exercise.get("secondary_muscle_group_ids", []))
                                exercise_id = existing_exercise.get("id")
                            else:
                                existing_name = existing_exercise.name
                                existing_primary = set(existing_exercise.primary_muscle_group_ids or [])
                                existing_secondary = set(existing_exercise.secondary_muscle_group_ids or [])
                                exercise_id = existing_exercise.id
                            
                            # Check if anything changed
                            needs_update = (
                                existing_name != exercise_name or
                                existing_primary != set(primary_mg_ids) or
                                existing_secondary != set(secondary_mg_ids)
                            )
                            
                            if needs_update:
                                # Update exercise
                                try:
                                    update_data = ExerciseUpdate(
                                        name=exercise_name if existing_name != exercise_name else None,
                                        primary_muscle_group_ids=primary_mg_ids if existing_primary != set(primary_mg_ids) else None,
                                        secondary_muscle_group_ids=secondary_mg_ids if existing_secondary != set(secondary_mg_ids) else None
                                    )
                                    await update_exercise_with_muscle_groups(
                                        db=db,
                                        exercise_id=exercise_id,
                                        exercise_data=update_data
                                    )
                                    await db.commit()
                                    updated_count += 1
                                except Exception as e:
                                    await db.rollback()
                                    errors.append(f"Exercise '{exercise_name}': Failed to update - {str(e)}")
                            else:
                                skipped_count += 1
                        else:
                            # New exercise - create it
                            try:
                                create_data = ExerciseCreate(
                                    name=exercise_name,
                                    primary_muscle_group_ids=primary_mg_ids,
                                    secondary_muscle_group_ids=secondary_mg_ids,
                                    enabled=True  # New exercises from Wger are enabled by default
                                )
                                await create_exercise_with_muscle_groups(db=db, exercise_data=create_data)
                                await db.commit()
                                # Refresh the existing exercise map to include the newly created exercise
                                existing_exercise_map[exercise_name.lower()] = cast(ExerciseRead, await crud_exercises.get(
                                    db=db,
                                    name=exercise_name,
                                    schema_to_select=ExerciseRead
                                ))
                                created_count += 1
                            except sqlalchemy_exc.IntegrityError as e:
                                # Handle duplicate key errors - exercise might have been created by another process
                                await db.rollback()
                                # Check if exercise exists now (might have been created concurrently)
                                existing_check = await crud_exercises.get(
                                    db=db,
                                    name=exercise_name,
                                    schema_to_select=ExerciseRead
                                )
                                if existing_check:
                                    # Exercise exists, treat as skipped
                                    existing_exercise_map[exercise_name.lower()] = cast(ExerciseRead, existing_check)
                                    skipped_count += 1
                                else:
                                    errors.append(f"Exercise '{exercise_name}': Duplicate key error - {str(e)}")
                            except Exception as e:
                                await db.rollback()
                                errors.append(f"Exercise '{exercise_name}': Failed to create - {str(e)}")
                            
                    except Exception as e:
                        await db.rollback()
                        errors.append(f"Error processing exercise: {str(e)}")
                        continue
                
                exercises_next = exercises_data.get("next")
            except Exception as e:
                await db.rollback()
                errors.append(f"Failed to fetch exercises from Wger API: {str(e)}")
                break
        
        # Final commit for any remaining changes
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            errors.append(f"Failed to commit final changes: {str(e)}")
        
        return {
            "message": "Wger sync completed",
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "muscle_groups_created": muscle_groups_created,
            "errors": errors[:50]  # Limit errors to first 50
        }

