from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_exercise_entry import crud_exercise_entry
from ...crud.crud_set_entry import crud_set_entry
from ...crud.crud_workout_session import crud_workout_session
from ...schemas.set_entry import SetEntryRead, SetEntryUpdate

router = APIRouter(tags=["set-entries"])


@router.patch("/set-entry/{set_id}", response_model=SetEntryRead)
async def update_set_entry(
    request: Request,
    set_id: int,
    set_update: SetEntryUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> SetEntryRead:
    """
    Update a set entry.

    Updates a set entry. The set must belong to an exercise entry that is part of
    a workout session owned by the authenticated user.

    **Path Parameters:**
    - `set_id` (int): The ID of the set entry to update.

    **Request Body:**
    - Any fields from SetEntryUpdate (weight_kg, reps, rir, rpe, etc.)

    **Returns:**
    - `SetEntryRead`: The updated set entry.

    **Raises:**
    - `NotFoundException`: If the set entry is not found or doesn't belong to the user's session.
    """
    # Verify set exists
    set_entry = await crud_set_entry.get(db=db, id=set_id)
    if set_entry is None:
        raise NotFoundException("Set entry not found")

    # Get exercise entry to verify ownership
    entry_id = (
        set_entry.exercise_entry_id if hasattr(set_entry, "exercise_entry_id") else set_entry["exercise_entry_id"]
    )
    entry = await crud_exercise_entry.get(db=db, id=entry_id)
    if entry is None:
        raise NotFoundException("Exercise entry not found")

    entry_session_id = entry.workout_session_id if hasattr(entry, "workout_session_id") else entry["workout_session_id"]
    session = await crud_workout_session.get(db=db, id=entry_session_id, user_id=current_user["id"])
    if session is None:
        raise NotFoundException("Set entry not found or access denied")

    # Update set
    update_dict = set_update.model_dump(exclude_unset=True)
    await crud_set_entry.update(db=db, object=update_dict, id=set_id)
    await db.commit()

    # Fetch updated set
    set_read = await crud_set_entry.get(
        db=db,
        id=set_id,
        schema_to_select=SetEntryRead,
        return_as_model=True,
    )
    if set_read is None:
        raise NotFoundException("Updated set entry not found")

    if isinstance(set_read, dict):
        return SetEntryRead(**set_read)
    elif hasattr(set_read, "model_dump"):
        return set_read
    else:
        set_dict = {
            "id": set_read.id,
            "exercise_entry_id": set_read.exercise_entry_id,
            "set_number": set_read.set_number,
            "weight_kg": set_read.weight_kg,
            "reps": set_read.reps,
            "rir": set_read.rir,
            "rpe": set_read.rpe,
            "percentage_of_1rm": set_read.percentage_of_1rm,
            "rest_seconds": set_read.rest_seconds,
            "tempo": set_read.tempo,
            "notes": set_read.notes,
            "is_warmup": set_read.is_warmup,
            "created_at": set_read.created_at if hasattr(set_read, "created_at") else None,
        }
        return SetEntryRead(**set_dict)
