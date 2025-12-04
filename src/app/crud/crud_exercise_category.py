from fastcrud import FastCRUD

from ..models.exercise_category import ExerciseCategoryModel
from ..schemas.exercise_category import ExerciseCategoryCreate, ExerciseCategoryRead, ExerciseCategoryUpdate

CRUDExerciseCategory = FastCRUD[
    ExerciseCategoryModel,
    ExerciseCategoryCreate,
    ExerciseCategoryUpdate,
    ExerciseCategoryUpdate,
    dict,
    ExerciseCategoryRead,
]
crud_exercise_category = CRUDExerciseCategory(ExerciseCategoryModel)
