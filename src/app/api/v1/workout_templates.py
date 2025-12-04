from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user, get_optional_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_workout_template import crud_workout_template
from ...schemas.workout_template import WorkoutTemplateCreate, WorkoutTemplateRead, WorkoutTemplateUpdate

router = APIRouter(tags=["workout-templates"])


@router.post("/workout-template", response_model=WorkoutTemplateRead, status_code=201)
async def create_workout_template(
    request: Request,
    template: WorkoutTemplateCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> WorkoutTemplateRead:
    """Create a new workout template."""
    # Set user_id if not provided
    if template.user_id is None:
        template.user_id = current_user["id"]
    elif template.user_id != current_user["id"]:
        raise NotFoundException("Cannot create template for another user")

    created = await crud_workout_template.create(db=db, object=template)
    await db.commit()

    if isinstance(created, dict):
        return WorkoutTemplateRead(**created)
    return WorkoutTemplateRead.model_validate(created)


@router.get("/workout-templates", response_model=PaginatedListResponse[WorkoutTemplateRead])
async def get_workout_templates(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict | None, Depends(get_optional_user)] = None,
    include_public: bool = True,
    page: int = 1,
    items_per_page: int = 20,
) -> dict[str, Any]:
    """Get workout templates (user's own and public ones)."""
    user_templates_data = await crud_workout_template.get_multi(
        db=db,
        offset=0,
        limit=10000,
        schema_to_select=WorkoutTemplateRead,
        user_id=current_user["id"] if current_user else None,
    )

    # Get public templates if requested
    public_templates_data = (
        await crud_workout_template.get_multi(
            db=db,
            offset=0,
            limit=10000,
            schema_to_select=WorkoutTemplateRead,
            is_public=True,
        )
        if include_public
        else {"data": []}
    )

    # Combine and paginate
    all_templates = user_templates_data.get("data", []) + public_templates_data.get("data", [])
    total_count = len(all_templates)

    start = compute_offset(page, items_per_page)
    end = start + items_per_page
    paginated_templates = all_templates[start:end]
    has_more = end < total_count

    return {
        "data": paginated_templates,
        "total_count": total_count,
        "has_more": has_more,
        "page": page,
        "items_per_page": items_per_page,
    }


@router.get("/workout-template/{template_id}", response_model=WorkoutTemplateRead)
async def get_workout_template(
    request: Request,
    template_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict | None, Depends(get_optional_user)] = None,
) -> WorkoutTemplateRead:
    """Get a specific workout template."""
    template = await crud_workout_template.get(db=db, id=template_id, schema_to_select=WorkoutTemplateRead)
    if template is None:
        raise NotFoundException("Workout template not found")

    # Check access (must be owner or public)
    template_user_id = template.user_id if hasattr(template, "user_id") else template.get("user_id")
    is_public = template.is_public if hasattr(template, "is_public") else template.get("is_public", False)

    if current_user and template_user_id == current_user["id"]:
        # Owner can access
        pass
    elif not is_public:
        # Not owner and not public
        raise NotFoundException("Workout template not found")

    return (
        WorkoutTemplateRead(**template) if isinstance(template, dict) else WorkoutTemplateRead.model_validate(template)
    )


@router.patch("/workout-template/{template_id}", response_model=WorkoutTemplateRead)
async def update_workout_template(
    request: Request,
    template_id: int,
    template_update: WorkoutTemplateUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> WorkoutTemplateRead:
    """Update a workout template (only owner can update)."""
    existing = await crud_workout_template.get(db=db, id=template_id)
    if existing is None:
        raise NotFoundException("Workout template not found")

    existing_user_id = existing.user_id if hasattr(existing, "user_id") else existing.get("user_id")
    if existing_user_id != current_user["id"]:
        raise NotFoundException("Cannot update template owned by another user")

    update_data = template_update.model_dump(exclude_unset=True)
    if update_data:
        await crud_workout_template.update(db=db, object=update_data, id=template_id)
        await db.commit()

    updated = await crud_workout_template.get(db=db, id=template_id, schema_to_select=WorkoutTemplateRead)
    return WorkoutTemplateRead(**updated) if isinstance(updated, dict) else WorkoutTemplateRead.model_validate(updated)


@router.delete("/workout-template/{template_id}")
async def delete_workout_template(
    request: Request,
    template_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a workout template (only owner can delete)."""
    existing = await crud_workout_template.get(db=db, id=template_id)
    if existing is None:
        raise NotFoundException("Workout template not found")

    existing_user_id = existing.user_id if hasattr(existing, "user_id") else existing.get("user_id")
    if existing_user_id != current_user["id"]:
        raise NotFoundException("Cannot delete template owned by another user")

    await crud_workout_template.db_delete(db=db, id=template_id)
    await db.commit()

    return {"message": "Workout template deleted"}


@router.post("/workout-template/{template_id}/apply", response_model=dict[str, Any], status_code=201)
async def apply_template_to_session(
    request: Request,
    template_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, Any]:
    """Apply a workout template to create a new workout session.

    This creates a new workout session based on the template,
    copying the structure but not the actual set data.
    """
    # Verify template exists and is accessible
    template = await crud_workout_template.get(db=db, id=template_id, schema_to_select=WorkoutTemplateRead)
    if template is None:
        raise NotFoundException("Workout template not found")

    template_user_id = template.user_id if hasattr(template, "user_id") else template.get("user_id")
    is_public = template.is_public if hasattr(template, "is_public") else template.get("is_public", False)

    if template_user_id != current_user["id"] and not is_public:
        raise NotFoundException("Workout template not found")

    # Note: This is a placeholder - actual implementation would need to:
    # 1. Create a new WorkoutSession
    # 2. Copy exercise entries from template (if templates had entries stored)
    # For now, templates are just metadata - actual structure would need to be stored separately
    # or we'd need a template_exercise_entry table

    return {
        "message": "Template application not fully implemented yet",
        "template_id": template_id,
        "note": (
            "Templates currently store metadata only. "
            "Full implementation requires template exercise structure storage."
        ),
    }
