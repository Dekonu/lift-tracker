from fastcrud import FastCRUD
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.exercise import Exercise, exercise_secondary_muscle_groups
from ..schemas.exercise import ExerciseCreate, ExerciseRead, ExerciseUpdate


CRUDExercise = FastCRUD[Exercise, ExerciseCreate, ExerciseUpdate, ExerciseUpdate, dict, ExerciseRead]
crud_exercises = CRUDExercise(Exercise)


async def create_exercise_with_muscle_groups(
    db: AsyncSession, exercise_data: ExerciseCreate
) -> ExerciseRead:
    """Create an exercise with its secondary muscle groups."""
    # Extract secondary muscle group IDs
    secondary_ids = exercise_data.secondary_muscle_group_ids
    exercise_dict = exercise_data.model_dump(exclude={"secondary_muscle_group_ids"})

    # Create the exercise
    created_exercise = await crud_exercises.create(db=db, object=exercise_dict)

    # Add secondary muscle groups if provided
    if secondary_ids:
        for muscle_group_id in secondary_ids:
            stmt = exercise_secondary_muscle_groups.insert().values(
                exercise_id=created_exercise.id, muscle_group_id=muscle_group_id
            )
            await db.execute(stmt)

    await db.commit()
    await db.refresh(created_exercise)

    # Fetch the exercise with relationships
    exercise = await crud_exercises.get(db=db, id=created_exercise.id, schema_to_select=ExerciseRead)
    if exercise is None:
        # Fallback: create ExerciseRead from created_exercise
        exercise_dict = {
            "id": created_exercise.id,
            "name": created_exercise.name if hasattr(created_exercise, "name") else "",
            "primary_muscle_group_id": (
                created_exercise.primary_muscle_group_id
                if hasattr(created_exercise, "primary_muscle_group_id")
                else 0
            ),
            "secondary_muscle_group_ids": secondary_ids,
        }
        return ExerciseRead(**exercise_dict)

    # Manually add secondary muscle group IDs
    if isinstance(exercise, dict):
        exercise["secondary_muscle_group_ids"] = secondary_ids
        return ExerciseRead(**exercise)
    else:
        exercise.secondary_muscle_group_ids = secondary_ids
        return exercise


async def update_exercise_with_muscle_groups(
    db: AsyncSession, exercise_id: int, exercise_data: ExerciseUpdate
) -> ExerciseRead | None:
    """Update an exercise and its secondary muscle groups."""
    exercise_dict = exercise_data.model_dump(exclude_unset=True, exclude={"secondary_muscle_group_ids"})
    secondary_ids = exercise_data.secondary_muscle_group_ids

    # Update the exercise if there are fields to update
    if exercise_dict:
        await crud_exercises.update(db=db, object=exercise_dict, id=exercise_id)

    # Update secondary muscle groups if provided
    if secondary_ids is not None:
        # Delete existing associations
        delete_stmt = exercise_secondary_muscle_groups.delete().where(
            exercise_secondary_muscle_groups.c.exercise_id == exercise_id
        )
        await db.execute(delete_stmt)

        # Add new associations
        if secondary_ids:
            for muscle_group_id in secondary_ids:
                insert_stmt = exercise_secondary_muscle_groups.insert().values(
                    exercise_id=exercise_id, muscle_group_id=muscle_group_id
                )
                await db.execute(insert_stmt)

    await db.commit()

    # Fetch updated exercise
    exercise = await crud_exercises.get(db=db, id=exercise_id, schema_to_select=ExerciseRead)
    if exercise is None:
        return None

    # Manually add secondary muscle group IDs if they were updated
    if secondary_ids is not None:
        if isinstance(exercise, dict):
            exercise["secondary_muscle_group_ids"] = secondary_ids
            return ExerciseRead(**exercise)
        else:
            exercise.secondary_muscle_group_ids = secondary_ids

    return exercise if not isinstance(exercise, dict) else ExerciseRead(**exercise)


async def get_exercise_with_muscle_groups(db: AsyncSession, exercise_id: int) -> ExerciseRead | None:
    """Get an exercise with its secondary muscle group IDs."""
    exercise = await crud_exercises.get(db=db, id=exercise_id, schema_to_select=ExerciseRead)
    if exercise is None:
        return None

    # Fetch secondary muscle group IDs
    from sqlalchemy import select

    stmt = select(exercise_secondary_muscle_groups.c.muscle_group_id).where(
        exercise_secondary_muscle_groups.c.exercise_id == exercise_id
    )
    result = await db.execute(stmt)
    secondary_ids = [row[0] for row in result.fetchall()]

    # Add secondary muscle group IDs to the exercise
    if isinstance(exercise, dict):
        exercise["secondary_muscle_group_ids"] = secondary_ids
        return ExerciseRead(**exercise)
    else:
        exercise.secondary_muscle_group_ids = secondary_ids

    return exercise if not isinstance(exercise, dict) else ExerciseRead(**exercise)

