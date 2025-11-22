from fastcrud import FastCRUD

from ..models.workout_template import WorkoutTemplate
from ..schemas.workout_template import WorkoutTemplateCreate, WorkoutTemplateRead, WorkoutTemplateUpdate

CRUDWorkoutTemplate = FastCRUD[WorkoutTemplate, WorkoutTemplateCreate, WorkoutTemplateUpdate, WorkoutTemplateUpdate, dict, WorkoutTemplateRead]
crud_workout_template = CRUDWorkoutTemplate(WorkoutTemplate)

