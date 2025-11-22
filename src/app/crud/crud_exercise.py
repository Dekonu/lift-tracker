from fastcrud import FastCRUD
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.exercise import Exercise
from ..schemas.exercise import ExerciseCreate, ExerciseCreateInternal, ExerciseRead, ExerciseUpdate


CRUDExercise = FastCRUD[Exercise, ExerciseCreateInternal, ExerciseUpdate, ExerciseUpdate, dict, ExerciseRead]
crud_exercises = CRUDExercise(Exercise)


async def create_exercise_with_muscle_groups(
    db: AsyncSession, exercise_data: ExerciseCreate
) -> ExerciseRead:
    """Create an exercise with its primary and secondary muscle groups."""
    # Extract muscle group IDs since they have init=False in the model
    primary_muscle_group_ids = exercise_data.primary_muscle_group_ids or []
    secondary_muscle_group_ids = exercise_data.secondary_muscle_group_ids or []
    
    # Create ExerciseCreateInternal without muscle group arrays
    # (they will be set after creation since the model fields have init=False)
    exercise_internal = ExerciseCreateInternal(
        name=exercise_data.name,
        enabled=exercise_data.enabled,
    )

    # Create the exercise
    created_exercise = await crud_exercises.create(db=db, object=exercise_internal)
    
    # Set muscle group IDs after creation
    created_exercise.primary_muscle_group_ids = primary_muscle_group_ids
    created_exercise.secondary_muscle_group_ids = secondary_muscle_group_ids
    
    await db.commit()
    await db.refresh(created_exercise)

    # Fetch the exercise with relationships
    exercise = await crud_exercises.get(db=db, id=created_exercise.id, schema_to_select=ExerciseRead)
    if exercise is None:
        # Fallback: create ExerciseRead from created_exercise
        exercise_dict = {
            "id": created_exercise.id,
            "name": created_exercise.name if hasattr(created_exercise, "name") else "",
            "primary_muscle_group_ids": (
                created_exercise.primary_muscle_group_ids
                if hasattr(created_exercise, "primary_muscle_group_ids")
                else []
            ),
            "secondary_muscle_group_ids": (
                created_exercise.secondary_muscle_group_ids
                if hasattr(created_exercise, "secondary_muscle_group_ids")
                else []
            ),
            "enabled": (
                created_exercise.enabled
                if hasattr(created_exercise, "enabled")
                else True
            ),
        }
        return ExerciseRead(**exercise_dict)

    return exercise if isinstance(exercise, ExerciseRead) else ExerciseRead(**exercise)


async def update_exercise_with_muscle_groups(
    db: AsyncSession, exercise_id: int, exercise_data: ExerciseUpdate
) -> ExerciseRead | None:
    """Update an exercise and its muscle groups."""
    # Extract muscle group IDs if provided (they have init=False in the model)
    exercise_dict = exercise_data.model_dump(exclude_unset=True)
    primary_muscle_group_ids = exercise_dict.pop("primary_muscle_group_ids", None)
    secondary_muscle_group_ids = exercise_dict.pop("secondary_muscle_group_ids", None)
    
    # Update the exercise with remaining fields
    if exercise_dict:
        await crud_exercises.update(db=db, object=exercise_dict, id=exercise_id)
    
    # Update muscle group IDs separately if provided
    exercise = await crud_exercises.get(db=db, id=exercise_id)
    if exercise:
        if primary_muscle_group_ids is not None:
            exercise.primary_muscle_group_ids = primary_muscle_group_ids
        if secondary_muscle_group_ids is not None:
            exercise.secondary_muscle_group_ids = secondary_muscle_group_ids
    
    await db.commit()

    # Fetch updated exercise
    exercise = await crud_exercises.get(db=db, id=exercise_id, schema_to_select=ExerciseRead)
    if exercise is None:
        return None

    return exercise if isinstance(exercise, ExerciseRead) else ExerciseRead(**exercise)


async def get_exercise_with_muscle_groups(db: AsyncSession, exercise_id: int) -> ExerciseRead | None:
    """Get an exercise with its secondary muscle group IDs."""
    exercise = await crud_exercises.get(db=db, id=exercise_id, schema_to_select=ExerciseRead)
    if exercise is None:
        return None

    # Secondary muscle group IDs are now stored directly in the exercise model
    return exercise if isinstance(exercise, ExerciseRead) else ExerciseRead(**exercise)

