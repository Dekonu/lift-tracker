from fastcrud import FastCRUD

from ..models.workout import Workout
from ..schemas.workout import WorkoutCreate, WorkoutRead, WorkoutUpdate

CRUDWorkout = FastCRUD[Workout, WorkoutCreate, WorkoutUpdate, WorkoutUpdate, dict, WorkoutRead]
crud_workouts = CRUDWorkout(Workout)

