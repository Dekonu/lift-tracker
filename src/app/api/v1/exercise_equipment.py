from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_equipment import crud_equipment
from ...crud.crud_exercise import crud_exercises
from ...crud.crud_exercise_equipment import crud_exercise_equipment
from ...schemas.equipment import EquipmentRead

router = APIRouter(tags=["exercise-equipment"])


@router.post("/exercise/{exercise_id}/equipment/{equipment_id}")
async def link_equipment_to_exercise(
    request: Request,
    exercise_id: int,
    equipment_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Link equipment to an exercise (admin only)."""
    if not current_user.get("is_superuser", False):
        raise NotFoundException("Only administrators can link equipment to exercises")

    # Verify exercise exists
    exercise = await crud_exercises.get(db=db, id=exercise_id)
    if exercise is None:
        raise NotFoundException("Exercise not found")

    # Verify equipment exists
    equipment = await crud_equipment.get(db=db, id=equipment_id)
    if equipment is None:
        raise NotFoundException("Equipment not found")

    # Link equipment
    await crud_exercise_equipment.link_equipment(db=db, exercise_id=exercise_id, equipment_id=equipment_id)
    await db.commit()

    return {"message": f"Equipment '{equipment.name}' linked to exercise '{exercise.name}'"}


@router.delete("/exercise/{exercise_id}/equipment/{equipment_id}")
async def unlink_equipment_from_exercise(
    request: Request,
    exercise_id: int,
    equipment_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Unlink equipment from an exercise (admin only)."""
    if not current_user.get("is_superuser", False):
        raise NotFoundException("Only administrators can unlink equipment from exercises")

    # Verify exercise exists
    exercise = await crud_exercises.get(db=db, id=exercise_id)
    if exercise is None:
        raise NotFoundException("Exercise not found")

    # Verify equipment exists
    equipment = await crud_equipment.get(db=db, id=equipment_id)
    if equipment is None:
        raise NotFoundException("Equipment not found")

    # Unlink equipment
    await crud_exercise_equipment.unlink_equipment(db=db, exercise_id=exercise_id, equipment_id=equipment_id)
    await db.commit()

    return {"message": f"Equipment '{equipment.name}' unlinked from exercise '{exercise.name}'"}


@router.get("/exercise/{exercise_id}/equipment", response_model=PaginatedListResponse[EquipmentRead])
async def get_exercise_equipment(
    request: Request,
    exercise_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 50,
) -> dict[str, Any]:
    """Get all equipment required for an exercise."""
    # Verify exercise exists
    exercise = await crud_exercises.get(db=db, id=exercise_id)
    if exercise is None:
        raise NotFoundException("Exercise not found")

    # Get equipment links
    equipment_links = await crud_exercise_equipment.get_by_exercise(db=db, exercise_id=exercise_id)

    # Get equipment details
    equipment_list = []
    for link in equipment_links:
        equipment_id = link.equipment_id if hasattr(link, "equipment_id") else link["equipment_id"]
        equipment = await crud_equipment.get(db=db, id=equipment_id, schema_to_select=EquipmentRead)
        if equipment:
            equipment_list.append(equipment)

    # Paginate
    total = len(equipment_list)
    start = compute_offset(page, items_per_page)
    end = start + items_per_page
    paginated_equipment = equipment_list[start:end]

    return {
        "data": paginated_equipment,
        "total": total,
        "page": page,
        "items_per_page": items_per_page,
        "pages": (total + items_per_page - 1) // items_per_page if total > 0 else 0,
    }
