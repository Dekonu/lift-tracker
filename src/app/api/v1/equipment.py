import csv
import io
from typing import Annotated, Any, cast

import httpx
from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user, get_optional_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_equipment import crud_equipment
from ...schemas.equipment import EquipmentCreate, EquipmentRead, EquipmentUpdate

router = APIRouter(tags=["equipment"])


@router.post("/equipment", response_model=EquipmentRead, status_code=201)
async def create_equipment(
    request: Request,
    equipment: EquipmentCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> EquipmentRead:
    """Create a new equipment item (admin only)."""
    if not current_user.get("is_superuser", False):
        raise NotFoundException("Only administrators can create equipment")

    # Check if equipment already exists
    existing = await crud_equipment.get(db=db, name=equipment.name)
    if existing:
        raise DuplicateValueException(f"Equipment '{equipment.name}' already exists")

    created = await crud_equipment.create(db=db, object=equipment)
    await db.commit()

    return EquipmentRead(**created) if isinstance(created, dict) else EquipmentRead.model_validate(created)


@router.get("/equipment", response_model=PaginatedListResponse[EquipmentRead])
async def get_equipment(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict | None, Depends(get_optional_user)] = None,
    page: int = 1,
    items_per_page: int = 50,
    enabled: bool | None = None,
) -> dict[str, Any]:
    """Get all equipment. Outside admin dashboard, only enabled equipment is returned."""
    # If user is not a superuser, only return enabled equipment
    if current_user is None or not current_user.get("is_superuser", False):
        enabled = True

    filters = {}
    if enabled is not None:
        filters["enabled"] = enabled

    equipment_data = await crud_equipment.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=EquipmentRead,
        **filters,
    )

    return paginated_response(crud_data=equipment_data, page=page, items_per_page=items_per_page)


@router.get("/equipment/{equipment_id}", response_model=EquipmentRead)
async def get_equipment_item(
    request: Request,
    equipment_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> EquipmentRead:
    """Get a specific equipment item."""
    equipment = await crud_equipment.get(db=db, id=equipment_id, schema_to_select=EquipmentRead)
    if equipment is None:
        raise NotFoundException("Equipment not found")

    return EquipmentRead(**equipment) if isinstance(equipment, dict) else EquipmentRead.model_validate(equipment)


@router.patch("/equipment/{equipment_id}", response_model=EquipmentRead)
async def update_equipment(
    request: Request,
    equipment_id: int,
    equipment_update: EquipmentUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> EquipmentRead:
    """Update equipment (admin only)."""
    if not current_user.get("is_superuser", False):
        raise NotFoundException("Only administrators can update equipment")

    existing = await crud_equipment.get(db=db, id=equipment_id)
    if existing is None:
        raise NotFoundException("Equipment not found")

    update_data = equipment_update.model_dump(exclude_unset=True)
    if update_data:
        await crud_equipment.update(db=db, object=update_data, id=equipment_id)
        await db.commit()

    updated = await crud_equipment.get(db=db, id=equipment_id, schema_to_select=EquipmentRead)
    return EquipmentRead(**updated) if isinstance(updated, dict) else EquipmentRead.model_validate(updated)


@router.delete("/equipment/{equipment_id}")
async def delete_equipment(
    request: Request,
    equipment_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete equipment (admin only)."""
    if not current_user.get("is_superuser", False):
        raise NotFoundException("Only administrators can delete equipment")

    existing = await crud_equipment.get(db=db, id=equipment_id)
    if existing is None:
        raise NotFoundException("Equipment not found")

    await crud_equipment.db_delete(db=db, id=equipment_id)
    await db.commit()

    return {"message": "Equipment deleted"}


@router.get("/equipment/export")
async def export_equipment(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> StreamingResponse:
    """Export all equipment as CSV (admin only)."""
    if not current_user.get("is_superuser", False):
        raise NotFoundException("Only administrators can export equipment")

    # Get all equipment
    equipment_data = await crud_equipment.get_multi(
        db=db,
        offset=0,
        limit=10000,
        schema_to_select=EquipmentRead,
    )
    equipment_list = equipment_data.get("data", [])

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["name", "description", "enabled"])

    # Write data
    for equipment in equipment_list:
        if isinstance(equipment, dict):
            name = equipment.get("name", "")
            description = equipment.get("description", "") or ""
            enabled = equipment.get("enabled", True)
        else:
            name = equipment.name
            description = equipment.description or ""
            enabled = getattr(equipment, "enabled", True)

        writer.writerow([name, description, "true" if enabled else "false"])

    output.seek(0)

    # Return as downloadable CSV
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=equipment_export.csv"},
    )


@router.post("/equipment/import")
async def import_equipment(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Import equipment from CSV file with change data capture (CDC).

    Only equipment that is new or changed will be created/updated.
    No equipment will be deleted.
    """
    if not current_user.get("is_superuser", False):
        raise NotFoundException("Only administrators can import equipment")

    # Validate file type
    if not file.filename.endswith(".csv"):
        raise NotFoundException("File must be a CSV file")

    # Read and parse CSV
    contents = await file.read()
    csv_content = contents.decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(csv_content))

    # Get all existing equipment
    equipment_data = await crud_equipment.get_multi(
        db=db,
        offset=0,
        limit=10000,
        schema_to_select=EquipmentRead,
    )
    existing_equipment = equipment_data.get("data", [])

    # Create a map of existing equipment by name (case-insensitive)
    existing_equipment_map: dict[str, EquipmentRead] = {}
    for eq in existing_equipment:
        if isinstance(eq, dict):
            name = eq.get("name", "")
        else:
            name = eq.name
        existing_equipment_map[name.lower()] = cast(EquipmentRead, eq)

    created_count = 0
    updated_count = 0
    skipped_count = 0
    errors: list[str] = []

    # Process each row
    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is header
        try:
            name = row.get("name", "").strip()
            if not name:
                skipped_count += 1
                continue

            description = row.get("description", "").strip() or None
            enabled_str = row.get("enabled", "true").strip().lower()
            enabled = enabled_str in ("true", "1", "yes", "enabled")

            # Check if equipment already exists
            existing = existing_equipment_map.get(name.lower())

            if existing:
                # Update existing equipment
                update_data: dict[str, Any] = {}
                if isinstance(existing, dict):
                    existing_name = existing.get("name", "")
                    existing_description = existing.get("description")
                    existing_enabled = existing.get("enabled", True)
                else:
                    existing_name = existing.name
                    existing_description = existing.description
                    existing_enabled = getattr(existing, "enabled", True)

                if description != existing_description:
                    update_data["description"] = description
                if enabled != existing_enabled:
                    update_data["enabled"] = enabled

                if update_data:
                    await crud_equipment.update(db=db, object=update_data, name=existing_name)
                    await db.commit()
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                # Create new equipment
                try:
                    new_equipment = EquipmentCreate(name=name, description=description, enabled=enabled)
                    await crud_equipment.create(db=db, object=new_equipment)
                    await db.commit()
                    created_count += 1
                    # Add to map to avoid duplicates in same import
                    existing_equipment_map[name.lower()] = cast(
                        EquipmentRead, {"name": name, "description": description, "enabled": enabled}
                    )
                except sqlalchemy_exc.IntegrityError:
                    await db.rollback()
                    # Equipment might have been created by another process, skip
                    skipped_count += 1
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            await db.rollback()

    return {
        "message": "Import completed",
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "errors": errors,
    }


@router.post("/equipment/sync-wger")
async def sync_equipment_from_wger(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    full_sync: bool = Query(default=False, description="If True, truncates all equipment and reloads from Wger"),
) -> dict[str, Any]:
    """Sync equipment from Wger API (https://wger.de/api/v2/equipment/).

    Fetches all equipment from Wger API and creates/updates equipment.

    Args:
        full_sync: If True, truncates all equipment and reloads from Wger.
                   If False, uses change data capture - only new or changed equipment is created/updated.
    """
    if not current_user.get("is_superuser", False):
        raise NotFoundException("Only administrators can sync equipment from Wger")

    WGER_API_BASE = "https://wger.de/api/v2"

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Handle full sync - truncate all equipment
        if full_sync:
            equipment_data = await crud_equipment.get_multi(
                db=db,
                offset=0,
                limit=10000,
            )
            all_equipment = equipment_data.get("data", [])
            for eq in all_equipment:
                if isinstance(eq, dict):
                    eq_id = eq.get("id")
                else:
                    eq_id = eq.id
                if eq_id:
                    await crud_equipment.db_delete(db=db, id=eq_id)

            await db.commit()
            existing_equipment_map: dict[str, EquipmentRead] = {}
        else:
            # Get all existing equipment for CDC
            equipment_data = await crud_equipment.get_multi(
                db=db,
                offset=0,
                limit=10000,
                schema_to_select=EquipmentRead,
            )
            existing_equipment = equipment_data.get("data", [])
            existing_equipment_map: dict[str, EquipmentRead] = {}
            for eq in existing_equipment:
                if isinstance(eq, dict):
                    name = eq.get("name", "")
                else:
                    name = eq.name
                existing_equipment_map[name.lower()] = cast(EquipmentRead, eq)

        # Fetch all equipment from Wger
        equipment_url = f"{WGER_API_BASE}/equipment/"
        equipment_next = equipment_url

        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors: list[str] = []

        while equipment_next:
            try:
                equipment_response = await client.get(equipment_next)
                equipment_response.raise_for_status()
                equipment_data = equipment_response.json()

                for wger_equipment in equipment_data.get("results", []):
                    try:
                        equipment_name = wger_equipment.get("name", "").strip()
                        if not equipment_name:
                            continue

                        # Check if equipment already exists
                        existing = existing_equipment_map.get(equipment_name.lower())

                        if existing:
                            # Update existing equipment (if needed)
                            if isinstance(existing, dict):
                                existing.get("enabled", True)
                            else:
                                getattr(existing, "enabled", True)

                            # Only update if enabled status changed
                            # (Wger doesn't have enabled field, so we keep existing)
                            # For now, we'll skip updates unless we need to change something
                            skipped_count += 1
                        else:
                            # Create new equipment
                            try:
                                new_equipment = EquipmentCreate(name=equipment_name, description=None, enabled=True)
                                await crud_equipment.create(db=db, object=new_equipment)
                                await db.commit()
                                created_count += 1
                                # Add to map to avoid duplicates
                                existing_equipment_map[equipment_name.lower()] = cast(
                                    EquipmentRead, {"name": equipment_name, "enabled": True}
                                )
                            except sqlalchemy_exc.IntegrityError:
                                await db.rollback()
                                # Equipment might have been created by another process
                                skipped_count += 1
                    except Exception as e:
                        errors.append(f"Error processing equipment '{equipment_name}': {str(e)}")
                        await db.rollback()

                equipment_next = equipment_data.get("next")
            except Exception as e:
                return {
                    "message": "Failed to fetch equipment from Wger API",
                    "error": str(e),
                    "created": created_count,
                    "updated": updated_count,
                    "skipped": skipped_count,
                    "errors": errors,
                }

        return {
            "message": "Sync completed",
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "errors": errors,
        }
