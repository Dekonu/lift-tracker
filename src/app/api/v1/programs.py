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


@router.post("/program", response_model=ProgramRead, status_code=201)
async def create_program(
    request: Request,
    program: ProgramCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ProgramRead:
    """Create a new training program."""
    # Set user_id if not provided
    if program.user_id is None:
        program.user_id = current_user["id"]
    elif program.user_id != current_user["id"]:
        raise NotFoundException("Cannot create program for another user")
    
    created = await crud_program.create(db=db, object=program)
    await db.commit()
    
    return ProgramRead(**created) if isinstance(created, dict) else ProgramRead.model_validate(created)


@router.get("/programs", response_model=PaginatedListResponse[ProgramRead])
async def get_programs(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict | None, Depends(get_current_user)],
    include_public: bool = True,
    page: int = 1,
    items_per_page: int = 20,
) -> dict[str, Any]:
    """Get programs (user's own and public ones)."""
    # Get user's programs
    user_programs_data = await crud_program.get_multi(
        db=db,
        offset=0,
        limit=10000,
        schema_to_select=ProgramRead,
        user_id=current_user["id"] if current_user else None,
    )
    
    # Get public programs if requested
    public_programs_data = await crud_program.get_multi(
        db=db,
        offset=0,
        limit=10000,
        schema_to_select=ProgramRead,
        is_public=True,
    ) if include_public else {"data": []}
    
    # Combine and paginate
    all_programs = user_programs_data.get("data", []) + public_programs_data.get("data", [])
    total_count = len(all_programs)
    
    start = compute_offset(page, items_per_page)
    end = start + items_per_page
    paginated_programs = all_programs[start:end]
    has_more = end < total_count
    
    return {
        "data": paginated_programs,
        "total_count": total_count,
        "has_more": has_more,
        "page": page,
        "items_per_page": items_per_page,
    }


@router.get("/program/{program_id}", response_model=ProgramRead)
async def get_program(
    request: Request,
    program_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ProgramRead:
    """Get a specific program."""
    program = await crud_program.get(db=db, id=program_id, schema_to_select=ProgramRead)
    if program is None:
        raise NotFoundException("Program not found")
    
    # Check access (must be owner or public)
    program_user_id = program.user_id if hasattr(program, "user_id") else program.get("user_id")
    is_public = program.is_public if hasattr(program, "is_public") else program.get("is_public", False)
    
    if program_user_id != current_user["id"] and not is_public:
        raise NotFoundException("Program not found")
    
    return ProgramRead(**program) if isinstance(program, dict) else ProgramRead.model_validate(program)


@router.patch("/program/{program_id}", response_model=ProgramRead)
async def update_program(
    request: Request,
    program_id: int,
    program_update: ProgramUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ProgramRead:
    """Update a program (only owner can update)."""
    existing = await crud_program.get(db=db, id=program_id)
    if existing is None:
        raise NotFoundException("Program not found")
    
    existing_user_id = existing.user_id if hasattr(existing, "user_id") else existing.get("user_id")
    if existing_user_id != current_user["id"]:
        raise NotFoundException("Cannot update program owned by another user")
    
    update_data = program_update.model_dump(exclude_unset=True)
    if update_data:
        await crud_program.update(db=db, object=update_data, id=program_id)
        await db.commit()
    
    updated = await crud_program.get(db=db, id=program_id, schema_to_select=ProgramRead)
    return ProgramRead(**updated) if isinstance(updated, dict) else ProgramRead.model_validate(updated)


@router.delete("/program/{program_id}")
async def delete_program(
    request: Request,
    program_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a program (only owner can delete)."""
    existing = await crud_program.get(db=db, id=program_id)
    if existing is None:
        raise NotFoundException("Program not found")
    
    existing_user_id = existing.user_id if hasattr(existing, "user_id") else existing.get("user_id")
    if existing_user_id != current_user["id"]:
        raise NotFoundException("Cannot delete program owned by another user")
    
    await crud_program.db_delete(db=db, id=program_id)
    await db.commit()
    
    return {"message": "Program deleted"}


@router.post("/program/{program_id}/week", response_model=ProgramWeekRead, status_code=201)
async def add_week_to_program(
    request: Request,
    program_id: int,
    week: ProgramWeekCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ProgramWeekRead:
    """Add a week to a program."""
    # Verify program exists and user owns it
    program = await crud_program.get(db=db, id=program_id)
    if program is None:
        raise NotFoundException("Program not found")
    
    program_user_id = program.user_id if hasattr(program, "user_id") else program.get("user_id")
    if program_user_id != current_user["id"]:
        raise NotFoundException("Cannot modify program owned by another user")
    
    # Set program_id
    week_data = week.model_dump()
    week_data["program_id"] = program_id
    
    created = await crud_program_week.create(db=db, object=week_data)
    await db.commit()
    
    return ProgramWeekRead(**created) if isinstance(created, dict) else ProgramWeekRead.model_validate(created)


@router.get("/program/{program_id}/weeks", response_model=PaginatedListResponse[ProgramWeekRead])
async def get_program_weeks(
    request: Request,
    program_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    items_per_page: int = 50,
) -> dict[str, Any]:
    """Get all weeks for a program."""
    # Verify program exists and is accessible
    program = await crud_program.get(db=db, id=program_id)
    if program is None:
        raise NotFoundException("Program not found")
    
    program_user_id = program.user_id if hasattr(program, "user_id") else program.get("user_id")
    is_public = program.is_public if hasattr(program, "is_public") else program.get("is_public", False)
    
    if program_user_id != current_user["id"] and not is_public:
        raise NotFoundException("Program not found")
    
    weeks_data = await crud_program_week.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=ProgramWeekRead,
        program_id=program_id,
    )
    
    return paginated_response(crud_data=weeks_data, page=page, items_per_page=items_per_page)

