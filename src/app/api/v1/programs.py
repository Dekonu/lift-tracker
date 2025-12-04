from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_program import crud_program
from ...crud.crud_program_week import crud_program_week
from ...schemas.program import ProgramCreate, ProgramRead, ProgramUpdate
from ...schemas.program_week import ProgramWeekCreate, ProgramWeekRead

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

    program_read = await crud_program.get(
        db=db,
        id=program_id,
        schema_to_select=ProgramRead,
        return_as_model=True,
    )
    if program_read is None:
        raise NotFoundException("Updated program not found")

    return ProgramRead(**program_read) if isinstance(program_read, dict) else ProgramRead.model_validate(program_read)
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
