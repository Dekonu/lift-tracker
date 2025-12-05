from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...api.dependencies import get_current_user, get_optional_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_template_exercise_entry import crud_template_exercise_entry
from ...crud.crud_template_set_entry import crud_template_set_entry
from ...crud.crud_workout_template import crud_workout_template
from ...models.template_exercise_entry import TemplateExerciseEntry
from ...models.template_set_entry import TemplateSetEntry
from ...models.workout_template import WorkoutTemplate
from ...schemas.template_exercise_entry import TemplateExerciseEntryCreate
from ...schemas.template_set_entry import TemplateSetEntryCreate
from ...schemas.workout_template import WorkoutTemplateCreate, WorkoutTemplateRead, WorkoutTemplateUpdate

# Note: Schema rebuilds are handled in src/app/api/v1/__init__.py
# to ensure all forward references are resolved in the correct order

router = APIRouter(tags=["workout-templates"])


@router.post("/workout-template", response_model=WorkoutTemplateRead, status_code=201)
async def create_workout_template(
    request: Request,
    template: WorkoutTemplateCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> WorkoutTemplateRead:
    """Create a new workout template with exercises and sets."""
    # Validation happens automatically via Pydantic - if we get here, template is valid
    # Set user_id if not provided
    template_dict = template.model_dump(exclude={"template_exercises"})
    if template_dict.get("user_id") is None:
        template_dict["user_id"] = current_user["id"]
    elif template_dict.get("user_id") != current_user["id"]:
        raise NotFoundException("Cannot create template for another user")

    # Check if template name already exists for this user
    existing_template = await crud_workout_template.get(
        db=db, name=template_dict["name"], user_id=current_user["id"]
    )
    if existing_template:
        raise DuplicateValueException(f"Workout template with name '{template_dict['name']}' already exists")

    # Create the template (exclude template_exercises as it's not a model field)
    # FastCRUD expects a Pydantic model, so we create one without template_exercises
    # Create a simple Pydantic model with only the database fields
    class TemplateForDB(BaseModel):
        name: str
        description: str | None = None
        is_public: bool = False
        estimated_duration_minutes: int | None = None
        user_id: int | None = None
    
    template_create_obj = TemplateForDB(**template_dict)
    created_template = await crud_workout_template.create(db=db, object=template_create_obj)
    await db.flush()

    # Create template exercises and sets
    template_exercises_data = template.template_exercises or []
    for exercise_idx, exercise_data in enumerate(template_exercises_data):
        exercise_dict = exercise_data.model_dump(exclude={"template_sets"})
        exercise_dict["workout_template_id"] = created_template.id
        exercise_dict["order"] = exercise_data.order if exercise_data.order is not None else exercise_idx

        # Create exercise entry (template_sets is excluded, it's a relationship not a field)
        # Create a Pydantic model without template_sets for FastCRUD
        class ExerciseForDB(BaseModel):
            workout_template_id: int | None = None
            exercise_id: int
            notes: str | None = None
            order: int = 0
        
        exercise_create_obj = ExerciseForDB(**exercise_dict)
        created_exercise = await crud_template_exercise_entry.create(db=db, object=exercise_create_obj)
        await db.flush()

        # Create sets for this exercise
        sets_data = exercise_data.template_sets or []
        for set_idx, set_data in enumerate(sets_data):
            set_dict = set_data.model_dump()
            set_dict["template_exercise_entry_id"] = created_exercise.id
            set_dict["set_number"] = set_data.set_number if set_data.set_number else (set_idx + 1)

            # Create a Pydantic model for the set (TemplateSetEntryCreate is fine as it doesn't have relationships)
            set_create = TemplateSetEntryCreate(**set_dict)
            await crud_template_set_entry.create(db=db, object=set_create)

    await db.commit()

    # Fetch the complete template with relationships
    stmt = (
        select(WorkoutTemplate)
        .where(WorkoutTemplate.id == created_template.id)
        .options(
            selectinload(WorkoutTemplate.template_exercises).selectinload(TemplateExerciseEntry.template_sets)
        )
    )
    result = await db.execute(stmt)
    full_template = result.scalar_one_or_none()

    if full_template is None:
        raise NotFoundException("Created template not found")

    return WorkoutTemplateRead.model_validate(full_template)


@router.get("/workout-templates", response_model=PaginatedListResponse[WorkoutTemplateRead])
async def get_workout_templates(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict | None, Depends(get_optional_user)] = None,
    include_public: bool = True,
    page: int = 1,
    items_per_page: int = 20,
) -> dict[str, Any]:
    """Get workout templates (user's own and public ones) with exercises and sets."""
    # Build query for user templates
    user_id = current_user["id"] if current_user else None
    conditions = []
    if user_id:
        conditions.append(WorkoutTemplate.user_id == user_id)

    # Get user templates
    user_stmt = select(WorkoutTemplate)
    if conditions:
        from sqlalchemy import or_
        user_stmt = user_stmt.where(or_(*conditions))
    user_stmt = user_stmt.options(
        selectinload(WorkoutTemplate.template_exercises).selectinload(TemplateExerciseEntry.template_sets)
    )

    user_result = await db.execute(user_stmt)
    user_templates = user_result.scalars().all()

    # Get public templates if requested
    public_templates = []
    if include_public:
        public_stmt = (
            select(WorkoutTemplate)
            .where(WorkoutTemplate.is_public == True)  # noqa: E712
            .options(
                selectinload(WorkoutTemplate.template_exercises).selectinload(TemplateExerciseEntry.template_sets)
            )
        )
        if user_id:
            # Exclude user's own templates from public list (already in user_templates)
            public_stmt = public_stmt.where(WorkoutTemplate.user_id != user_id)
        public_result = await db.execute(public_stmt)
        public_templates = public_result.scalars().all()

    # Combine and paginate
    all_templates = list(user_templates) + list(public_templates)
    total_count = len(all_templates)

    start = compute_offset(page, items_per_page)
    end = start + items_per_page
    paginated_templates = all_templates[start:end]
    has_more = end < total_count

    # Convert to read models
    templates_data = [WorkoutTemplateRead.model_validate(t) for t in paginated_templates]

    return {
        "data": templates_data,
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
    """Get a specific workout template with exercises and sets."""
    # Fetch template with relationships
    stmt = (
        select(WorkoutTemplate)
        .where(WorkoutTemplate.id == template_id)
        .options(
            selectinload(WorkoutTemplate.template_exercises).selectinload(TemplateExerciseEntry.template_sets)
        )
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if template is None:
        raise NotFoundException("Workout template not found")

    # Check access (must be owner or public)
    template_user_id = template.user_id
    is_public = template.is_public

    if current_user and template_user_id == current_user["id"]:
        # Owner can access
        pass
    elif not is_public:
        # Not owner and not public
        raise NotFoundException("Workout template not found")

    return WorkoutTemplateRead.model_validate(template)


@router.patch("/workout-template/{template_id}", response_model=WorkoutTemplateRead)
async def update_workout_template(
    request: Request,
    template_id: int,
    template_update: WorkoutTemplateUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> WorkoutTemplateRead:
    """Update a workout template including exercises and sets (only owner can update)."""
    # Fetch template to check ownership and get existing exercises
    stmt = (
        select(WorkoutTemplate)
        .where(WorkoutTemplate.id == template_id)
        .options(
            selectinload(WorkoutTemplate.template_exercises).selectinload(TemplateExerciseEntry.template_sets)
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing is None:
        raise NotFoundException("Workout template not found")

    existing_user_id = existing.user_id
    if existing_user_id != current_user["id"]:
        raise NotFoundException("Cannot update template owned by another user")

    update_data = template_update.model_dump(exclude_unset=True)
    
    # Check if name is being updated and if it conflicts with another template
    if "name" in update_data:
        conflicting_template = await crud_workout_template.get(
            db=db, name=update_data["name"], user_id=current_user["id"]
        )
        if conflicting_template and conflicting_template.id != template_id:
            raise DuplicateValueException(f"Workout template with name '{update_data['name']}' already exists")
    
    # Handle template_exercises update if provided
    template_exercises_data = update_data.pop("template_exercises", None)
    
    # Update basic template fields
    if update_data:
        await crud_workout_template.update(db=db, object=update_data, id=template_id)
    
    # Handle exercises and sets update
    if template_exercises_data is not None:
        
        # Get existing exercise entry IDs
        existing_exercise_ids = {ex.id for ex in existing.template_exercises}
        
        # Process each exercise in the update
        new_exercise_ids = set()
        for exercise_data in template_exercises_data:
            exercise_dict = exercise_data if isinstance(exercise_data, dict) else exercise_data.model_dump()
            exercise_id = exercise_dict.get("id")  # If provided, this is an update
            
            if exercise_id and exercise_id in existing_exercise_ids:
                # Update existing exercise entry
                exercise_update_data = {
                    "exercise_id": exercise_dict.get("exercise_id"),
                    "notes": exercise_dict.get("notes"),
                    "order": exercise_dict.get("order"),
                }
                exercise_update_data = {k: v for k, v in exercise_update_data.items() if v is not None}
                
                if exercise_update_data:
                    await crud_template_exercise_entry.update(
                        db=db, object=exercise_update_data, id=exercise_id
                    )
                
                # Get existing exercise entry to update sets
                existing_exercise = next((ex for ex in existing.template_exercises if ex.id == exercise_id), None)
                if existing_exercise:
                    # Handle sets update
                    sets_data = exercise_dict.get("template_sets", [])
                    existing_set_ids = {s.id for s in existing_exercise.template_sets}
                    new_set_ids = set()
                    
                    for set_data in sets_data:
                        set_dict = set_data if isinstance(set_data, dict) else set_data.model_dump()
                        set_id = set_dict.get("id")  # If provided, this is an update
                        
                        if set_id and set_id in existing_set_ids:
                            # Update existing set
                            set_update_data = {
                                "set_number": set_dict.get("set_number"),
                                "weight_kg": set_dict.get("weight_kg"),
                                "reps": set_dict.get("reps"),
                                "rir": set_dict.get("rir"),
                                "rpe": set_dict.get("rpe"),
                                "percentage_of_1rm": set_dict.get("percentage_of_1rm"),
                                "rest_seconds": set_dict.get("rest_seconds"),
                                "tempo": set_dict.get("tempo"),
                                "notes": set_dict.get("notes"),
                                "is_warmup": set_dict.get("is_warmup"),
                            }
                            set_update_data = {k: v for k, v in set_update_data.items() if v is not None}
                            
                            if set_update_data:
                                await crud_template_set_entry.update(
                                    db=db, object=set_update_data, id=set_id
                                )
                            new_set_ids.add(set_id)
                        else:
                            # Create new set
                            set_create_data = TemplateSetEntryCreate(
                                template_exercise_entry_id=exercise_id,
                                set_number=set_dict.get("set_number", 1),
                                weight_kg=set_dict.get("weight_kg"),
                                reps=set_dict.get("reps"),
                                rir=set_dict.get("rir"),
                                rpe=set_dict.get("rpe"),
                                percentage_of_1rm=set_dict.get("percentage_of_1rm"),
                                rest_seconds=set_dict.get("rest_seconds"),
                                tempo=set_dict.get("tempo"),
                                notes=set_dict.get("notes"),
                                is_warmup=set_dict.get("is_warmup", False),
                            )
                            created_set = await crud_template_set_entry.create(db=db, object=set_create_data)
                            new_set_ids.add(created_set.id)
                    
                    # Delete sets that are no longer in the update
                    sets_to_delete = existing_set_ids - new_set_ids
                    for set_id in sets_to_delete:
                        await crud_template_set_entry.db_delete(db=db, id=set_id)
                
                new_exercise_ids.add(exercise_id)
            else:
                # Create new exercise entry
                exercise_create_data = TemplateExerciseEntryCreate(
                    workout_template_id=template_id,
                    exercise_id=exercise_dict.get("exercise_id"),
                    notes=exercise_dict.get("notes"),
                    order=exercise_dict.get("order", 0),
                    template_sets=[],
                )
                created_exercise = await crud_template_exercise_entry.create(db=db, object=exercise_create_data)
                new_exercise_ids.add(created_exercise.id)
                
                # Create sets for the new exercise
                sets_data = exercise_dict.get("template_sets", [])
                for set_data in sets_data:
                    set_dict = set_data if isinstance(set_data, dict) else set_data.model_dump()
                    set_create_data = TemplateSetEntryCreate(
                        template_exercise_entry_id=created_exercise.id,
                        set_number=set_dict.get("set_number", 1),
                        weight_kg=set_dict.get("weight_kg"),
                        reps=set_dict.get("reps"),
                        rir=set_dict.get("rir"),
                        rpe=set_dict.get("rpe"),
                        percentage_of_1rm=set_dict.get("percentage_of_1rm"),
                        rest_seconds=set_dict.get("rest_seconds"),
                        tempo=set_dict.get("tempo"),
                        notes=set_dict.get("notes"),
                        is_warmup=set_dict.get("is_warmup", False),
                    )
                    await crud_template_set_entry.create(db=db, object=set_create_data)
        
        # Delete exercises that are no longer in the update
        exercises_to_delete = existing_exercise_ids - new_exercise_ids
        for exercise_id in exercises_to_delete:
            await crud_template_exercise_entry.db_delete(db=db, id=exercise_id)
    
    await db.commit()

    # Fetch updated template with relationships
    stmt = (
        select(WorkoutTemplate)
        .where(WorkoutTemplate.id == template_id)
        .options(
            selectinload(WorkoutTemplate.template_exercises).selectinload(TemplateExerciseEntry.template_sets)
        )
    )
    result = await db.execute(stmt)
    updated = result.scalar_one_or_none()

    if updated is None:
        raise NotFoundException("Updated template not found")

    return WorkoutTemplateRead.model_validate(updated)


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
