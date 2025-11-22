from fastcrud import FastCRUD

from ..models.exercise_entry import ExerciseEntry
from ..schemas.exercise_entry import ExerciseEntryCreate, ExerciseEntryRead, ExerciseEntryUpdate

CRUDExerciseEntry = FastCRUD[ExerciseEntry, ExerciseEntryCreate, ExerciseEntryUpdate, ExerciseEntryUpdate, dict, ExerciseEntryRead]
crud_exercise_entry = CRUDExerciseEntry(ExerciseEntry)

