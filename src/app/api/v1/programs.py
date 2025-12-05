from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_program import crud_program
from ...crud.crud_program_week import crud_program_week
from ...crud.crud_program_day_assignment import crud_program_day_assignment
from ...models.program_day_assignment import ProgramDayAssignment
from ...schemas.program import ProgramCreate, ProgramRead, ProgramUpdate
from ...schemas.program_week import ProgramWeekCreate, ProgramWeekRead, ProgramWeekUpdate
from ...schemas.program_day_assignment import (
    ProgramDayAssignmentCreate,
    ProgramDayAssignmentRead,
    ProgramDayAssignmentUpdate,
)

router = APIRouter(tags=["programs"])

ProgramRead.model_rebuild()


@router.post("/program", response_model=ProgramRead, status_code=201)
async def create_program(
    request: Request,
    program: ProgramCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ProgramRead:
    """Create a new training program."""
    program_dict = program.model_dump()
    program_dict["user_id"] = current_user["id"]
    program_internal = ProgramCreate(**program_dict)

    created = await crud_program.create(db=db, object=program_internal)
    await db.commit()
    await db.refresh(created)

    program_read = await crud_program.get(
        db=db,
        id=created.id,
        schema_to_select=ProgramRead,
        return_as_model=True,
    )
    if program_read is None:
        raise NotFoundException("Created program not found")

    return ProgramRead(**program_read) if isinstance(program_read, dict) else ProgramRead.model_validate(program_read)


@router.get("/programs", response_model=PaginatedListResponse[ProgramRead])
async def get_programs(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    items_per_page: int = 20,
) -> dict[str, Any]:
    """Get all programs for the current user."""
    programs_data = await crud_program.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=ProgramRead,
        user_id=current_user["id"],
    )

    return paginated_response(crud_data=programs_data, page=page, items_per_page=items_per_page)


@router.get("/program/{program_id}", response_model=ProgramRead)
async def get_program(
    request: Request,
    program_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ProgramRead:
    """Get a specific program."""
    program = await crud_program.get(
        db=db,
        id=program_id,
        user_id=current_user["id"],
        schema_to_select=ProgramRead,
    )
    if program is None:
        raise NotFoundException("Program not found")

    if isinstance(program, dict):
        return ProgramRead(**program)
    else:
        return ProgramRead.model_validate(program)


@router.get("/program/{program_id}/weeks", response_model=PaginatedListResponse[ProgramWeekRead])
async def get_program_weeks(
    request: Request,
    program_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    items_per_page: int = 100,
) -> dict[str, Any]:
    """
    Get all weeks for a program.

    **Path Parameters:**
    - `program_id` (int): The ID of the program.

    **Returns:**
    - `PaginatedListResponse[ProgramWeekRead]`: Paginated list of program weeks.

    **Raises:**
    - `NotFoundException`: If the program is not found or doesn't belong to the user.
    """
    # Verify program exists and belongs to user
    program = await crud_program.get(db=db, id=program_id, user_id=current_user["id"])
    if program is None:
        raise NotFoundException("Program not found")

    # Get program weeks
    weeks_data = await crud_program_week.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=ProgramWeekRead,
        program_id=program_id,
    )

    return paginated_response(crud_data=weeks_data, page=page, items_per_page=items_per_page)


@router.post("/program/{program_id}/week", response_model=ProgramWeekRead, status_code=201)
async def add_week_to_program(
    request: Request,
    program_id: int,
    week: ProgramWeekCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ProgramWeekRead:
    """Add a week to a program."""
    # Verify program exists and belongs to user
    program = await crud_program.get(db=db, id=program_id, user_id=current_user["id"])
    if program is None:
        raise NotFoundException("Program not found")

    week_dict = week.model_dump()
    week_dict["program_id"] = program_id
    week_internal = ProgramWeekCreate(**week_dict)

    created = await crud_program_week.create(db=db, object=week_internal)
    await db.commit()
    await db.refresh(created)

    week_read = await crud_program_week.get(
        db=db,
        id=created.id,
        schema_to_select=ProgramWeekRead,
        return_as_model=True,
    )
    if week_read is None:
        raise NotFoundException("Created program week not found")

    return ProgramWeekRead(**week_read) if isinstance(week_read, dict) else ProgramWeekRead.model_validate(week_read)


@router.patch("/program/{program_id}/week/{week_id}", response_model=ProgramWeekRead)
async def update_program_week(
    request: Request,
    program_id: int,
    week_id: int,
    week_update: ProgramWeekUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ProgramWeekRead:
    """Update a program week."""
    # Verify program exists and belongs to user
    program = await crud_program.get(db=db, id=program_id, user_id=current_user["id"])
    if program is None:
        raise NotFoundException("Program not found")

    # Verify week exists and belongs to program
    week = await crud_program_week.get(db=db, id=week_id, program_id=program_id)
    if week is None:
        raise NotFoundException("Program week not found")

    update_dict = week_update.model_dump(exclude_unset=True)
    await crud_program_week.update(db=db, object=update_dict, id=week_id)
    await db.commit()

    week_read = await crud_program_week.get(
        db=db,
        id=week_id,
        schema_to_select=ProgramWeekRead,
        return_as_model=True,
    )
    if week_read is None:
        raise NotFoundException("Updated program week not found")

    return (
        ProgramWeekRead(**week_read)
        if isinstance(week_read, dict)
        else ProgramWeekRead.model_validate(week_read)
    )


@router.patch("/program/{program_id}", response_model=ProgramRead)
async def update_program(
    request: Request,
    program_id: int,
    program_update: ProgramUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ProgramRead:
    """Update a program."""
    program = await crud_program.get(db=db, id=program_id, user_id=current_user["id"])
    if program is None:
        raise NotFoundException("Program not found")

    update_dict = program_update.model_dump(exclude_unset=True)
    await crud_program.update(db=db, object=update_dict, id=program_id)
    await db.commit()

    program_read = await crud_program.get(
        db=db,
        id=program_id,
        schema_to_select=ProgramRead,
        return_as_model=True,
    )
    if program_read is None:
        raise NotFoundException("Updated program not found")

    return ProgramRead(**program_read) if isinstance(program_read, dict) else ProgramRead.model_validate(program_read)


@router.delete("/program/{program_id}", status_code=204)
async def delete_program(
    request: Request,
    program_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> None:
    """Delete a program."""
    program = await crud_program.get(db=db, id=program_id, user_id=current_user["id"])
    if program is None:
        raise NotFoundException("Program not found")

    await crud_program.db_delete(db=db, id=program_id)
    await db.commit()


# Day-based assignment endpoints (days 1-7, multiple templates per day)
@router.get("/program/{program_id}/days", response_model=PaginatedListResponse[ProgramDayAssignmentRead])
async def get_program_day_assignments(
    request: Request,
    program_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    week_number: int | None = None,
    page: int = 1,
    items_per_page: int = 100,
) -> dict[str, Any]:
    """Get all day assignments for a program, optionally filtered by week."""
    # Verify program exists and belongs to user
    program = await crud_program.get(db=db, id=program_id, user_id=current_user["id"])
    if program is None:
        raise NotFoundException("Program not found")

    # Build query filters
    filters = {"program_id": program_id}
    if week_number is not None:
        filters["week_number"] = week_number

    # Build query with relationship loading
    try:
        stmt = select(ProgramDayAssignment).where(ProgramDayAssignment.program_id == program_id)
        if week_number is not None:
            stmt = stmt.where(ProgramDayAssignment.week_number == week_number)
        stmt = stmt.options(selectinload(ProgramDayAssignment.workout_template))
        stmt = stmt.offset(compute_offset(page, items_per_page)).limit(items_per_page)

        result = await db.execute(stmt)
        assignments = result.scalars().all()

        # Create response data without nested template_exercises to avoid greenlet error
        assignments_data = []
        for assignment in assignments:
            assignment_dict = {
                "id": assignment.id,
                "program_id": assignment.program_id,
                "week_number": assignment.week_number,
                "day_number": assignment.day_number,
                "workout_template_id": assignment.workout_template_id,
                "order": assignment.order,
            }

            # Add workout_template if loaded (without template_exercises)
            if assignment.workout_template:
                from ...schemas.workout_template import WorkoutTemplateRead
                template_dict = {
                    "id": assignment.workout_template.id,
                    "name": assignment.workout_template.name,
                    "description": assignment.workout_template.description,
                    "is_public": assignment.workout_template.is_public,
                    "estimated_duration_minutes": assignment.workout_template.estimated_duration_minutes,
                    "user_id": assignment.workout_template.user_id,
                    "created_at": assignment.workout_template.created_at,
                    "updated_at": assignment.workout_template.updated_at,
                }
                assignment_dict["workout_template"] = WorkoutTemplateRead(**template_dict)

            assignments_data.append(ProgramDayAssignmentRead.model_validate(assignment_dict))

        # Get total count for pagination
        from sqlalchemy import func
        count_stmt = select(func.count(ProgramDayAssignment.id)).where(ProgramDayAssignment.program_id == program_id)
        if week_number is not None:
            count_stmt = count_stmt.where(ProgramDayAssignment.week_number == week_number)
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar_one()

        # Format as expected by paginated_response
        crud_data = {"data": assignments_data, "total_count": total_count}

        return paginated_response(crud_data=crud_data, page=page, items_per_page=items_per_page)
    except ProgrammingError as e:
        # If table doesn't exist, return empty result
        # This can happen if migration hasn't been run yet
        import logging
        logging.warning(f"Error fetching day assignments (table may not exist): {e}")
        crud_data = {"data": [], "total_count": 0}
        return paginated_response(crud_data=crud_data, page=page, items_per_page=items_per_page)


@router.post("/program/{program_id}/day", response_model=ProgramDayAssignmentRead, status_code=201)
async def add_day_assignment(
    request: Request,
    program_id: int,
    assignment: ProgramDayAssignmentCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ProgramDayAssignmentRead:
    """Add a workout template assignment to a specific day (1-7) in a program week.
    
    If an assignment with the same (program_id, week_number, day_number, workout_template_id, order)
    already exists, returns the existing assignment instead of creating a duplicate.
    If order is not specified or would cause a conflict, automatically finds the next available order.
    """
    # Verify program exists and belongs to user
    program = await crud_program.get(db=db, id=program_id, user_id=current_user["id"])
    if program is None:
        raise NotFoundException("Program not found")

    # Verify day_number is valid (1-7)
    if assignment.day_number < 1 or assignment.day_number > 7:
        raise NotFoundException("Day number must be between 1 and 7")

    # Check if assignment already exists with the same parameters
    existing = await crud_program_day_assignment.get(
        db=db,
        program_id=program_id,
        week_number=assignment.week_number,
        day_number=assignment.day_number,
        workout_template_id=assignment.workout_template_id,
        order=assignment.order,
    )

    if existing:
        # Return existing assignment
        stmt = (
            select(ProgramDayAssignment)
            .where(ProgramDayAssignment.id == existing.id)
            .options(selectinload(ProgramDayAssignment.workout_template))
        )
        result = await db.execute(stmt)
        assignment_obj = result.scalar_one_or_none()
        if assignment_obj is None:
            raise NotFoundException("Existing assignment not found")

        # Create response without nested template_exercises
        assignment_dict = {
            "id": assignment_obj.id,
            "program_id": assignment_obj.program_id,
            "week_number": assignment_obj.week_number,
            "day_number": assignment_obj.day_number,
            "workout_template_id": assignment_obj.workout_template_id,
            "order": assignment_obj.order,
        }

        if assignment_obj.workout_template:
            from ...schemas.workout_template import WorkoutTemplateRead
            template_dict = {
                "id": assignment_obj.workout_template.id,
                "name": assignment_obj.workout_template.name,
                "description": assignment_obj.workout_template.description,
                "is_public": assignment_obj.workout_template.is_public,
                "estimated_duration_minutes": assignment_obj.workout_template.estimated_duration_minutes,
                "user_id": assignment_obj.workout_template.user_id,
                "created_at": assignment_obj.workout_template.created_at,
                "updated_at": assignment_obj.workout_template.updated_at,
            }
            assignment_dict["workout_template"] = WorkoutTemplateRead(**template_dict)

        return ProgramDayAssignmentRead.model_validate(assignment_dict)

    # If order not specified or would conflict, find next available order
    if assignment.order == 0:
        # Find max order for this day/week combination
        stmt = (
            select(func.max(ProgramDayAssignment.order))
            .where(
                ProgramDayAssignment.program_id == program_id,
                ProgramDayAssignment.week_number == assignment.week_number,
                ProgramDayAssignment.day_number == assignment.day_number,
            )
        )
        result = await db.execute(stmt)
        max_order = result.scalar_one() or -1
        assignment.order = max_order + 1

    assignment_dict = assignment.model_dump()
    assignment_dict["program_id"] = program_id
    assignment_internal = ProgramDayAssignmentCreate(**assignment_dict)

    try:
        created = await crud_program_day_assignment.create(db=db, object=assignment_internal)
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        # If unique constraint violation, find next available order
        if "uq_program_day_assignment" in str(e.orig).lower() or "unique" in str(e.orig).lower():
            # Find max order for this specific template on this day
            stmt = (
                select(func.max(ProgramDayAssignment.order))
                .where(
                    ProgramDayAssignment.program_id == program_id,
                    ProgramDayAssignment.week_number == assignment.week_number,
                    ProgramDayAssignment.day_number == assignment.day_number,
                    ProgramDayAssignment.workout_template_id == assignment.workout_template_id,
                )
            )
            result = await db.execute(stmt)
            max_order = result.scalar_one() or -1
            assignment.order = max_order + 1

            assignment_dict = assignment.model_dump()
            assignment_dict["program_id"] = program_id
            assignment_dict["order"] = assignment.order
            assignment_internal = ProgramDayAssignmentCreate(**assignment_dict)
            created = await crud_program_day_assignment.create(db=db, object=assignment_internal)
            await db.commit()
        else:
            raise

    # Fetch with relationship (load workout_template but not nested template_exercises)
    stmt = (
        select(ProgramDayAssignment)
        .where(ProgramDayAssignment.id == created.id)
        .options(selectinload(ProgramDayAssignment.workout_template))
    )
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()

    if assignment is None:
        raise NotFoundException("Created day assignment not found")

    # Create response without nested template_exercises to avoid greenlet error
    assignment_dict = {
        "id": assignment.id,
        "program_id": assignment.program_id,
        "week_number": assignment.week_number,
        "day_number": assignment.day_number,
        "workout_template_id": assignment.workout_template_id,
        "order": assignment.order,
    }
    
    # Add workout_template if loaded (without template_exercises)
    if assignment.workout_template:
        from ...schemas.workout_template import WorkoutTemplateBase
        template_dict = {
            "id": assignment.workout_template.id,
            "name": assignment.workout_template.name,
            "description": assignment.workout_template.description,
            "is_public": assignment.workout_template.is_public,
            "estimated_duration_minutes": assignment.workout_template.estimated_duration_minutes,
            "user_id": assignment.workout_template.user_id,
            "created_at": assignment.workout_template.created_at,
            "updated_at": assignment.workout_template.updated_at,
        }
        from ...schemas.workout_template import WorkoutTemplateRead
        assignment_dict["workout_template"] = WorkoutTemplateRead(**template_dict)

    return ProgramDayAssignmentRead.model_validate(assignment_dict)


@router.patch("/program/{program_id}/day/{assignment_id}", response_model=ProgramDayAssignmentRead)
async def update_day_assignment(
    request: Request,
    program_id: int,
    assignment_id: int,
    assignment_update: ProgramDayAssignmentUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ProgramDayAssignmentRead:
    """Update a day assignment (e.g., change template or day)."""
    # Verify program exists and belongs to user
    program = await crud_program.get(db=db, id=program_id, user_id=current_user["id"])
    if program is None:
        raise NotFoundException("Program not found")

    # Verify assignment exists and belongs to program
    assignment = await crud_program_day_assignment.get(db=db, id=assignment_id, program_id=program_id)
    if assignment is None:
        raise NotFoundException("Day assignment not found")

    # Validate day_number if being updated
    if assignment_update.day_number is not None and (assignment_update.day_number < 1 or assignment_update.day_number > 7):
        raise NotFoundException("Day number must be between 1 and 7")

    update_dict = assignment_update.model_dump(exclude_unset=True)
    await crud_program_day_assignment.update(db=db, object=update_dict, id=assignment_id)
    await db.commit()

    # Fetch with relationship (load workout_template but not nested template_exercises)
    stmt = (
        select(ProgramDayAssignment)
        .where(ProgramDayAssignment.id == assignment_id)
        .options(selectinload(ProgramDayAssignment.workout_template))
    )
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()

    if assignment is None:
        raise NotFoundException("Updated day assignment not found")

    # Create response without nested template_exercises to avoid greenlet error
    assignment_dict = {
        "id": assignment.id,
        "program_id": assignment.program_id,
        "week_number": assignment.week_number,
        "day_number": assignment.day_number,
        "workout_template_id": assignment.workout_template_id,
        "order": assignment.order,
    }
    
    # Add workout_template if loaded (without template_exercises)
    if assignment.workout_template:
        from ...schemas.workout_template import WorkoutTemplateRead
        template_dict = {
            "id": assignment.workout_template.id,
            "name": assignment.workout_template.name,
            "description": assignment.workout_template.description,
            "is_public": assignment.workout_template.is_public,
            "estimated_duration_minutes": assignment.workout_template.estimated_duration_minutes,
            "user_id": assignment.workout_template.user_id,
            "created_at": assignment.workout_template.created_at,
            "updated_at": assignment.workout_template.updated_at,
        }
        assignment_dict["workout_template"] = WorkoutTemplateRead(**template_dict)

    return ProgramDayAssignmentRead.model_validate(assignment_dict)


@router.delete("/program/{program_id}/day/{assignment_id}", status_code=204)
async def delete_day_assignment(
    request: Request,
    program_id: int,
    assignment_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> None:
    """Delete a day assignment."""
    # Verify program exists and belongs to user
    program = await crud_program.get(db=db, id=program_id, user_id=current_user["id"])
    if program is None:
        raise NotFoundException("Program not found")

    # Verify assignment exists and belongs to program
    assignment = await crud_program_day_assignment.get(db=db, id=assignment_id, program_id=program_id)
    if assignment is None:
        raise NotFoundException("Day assignment not found")

    await crud_program_day_assignment.db_delete(db=db, id=assignment_id)
    await db.commit()
