from fastcrud import FastCRUD

from ..models.exercise_instance import ExerciseInstance
from ..schemas.exercise_instance import ExerciseInstanceCreate, ExerciseInstanceRead, ExerciseInstanceUpdate

CRUDExerciseInstance = FastCRUD[
    ExerciseInstance,
    ExerciseInstanceCreate,
    ExerciseInstanceUpdate,
    ExerciseInstanceUpdate,
    dict,
    ExerciseInstanceRead,
]
crud_exercise_instances = CRUDExerciseInstance(ExerciseInstance)
