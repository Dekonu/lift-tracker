from fastcrud import FastCRUD

from ..models.workout_session import WorkoutSession
from ..schemas.workout_session import WorkoutSessionCreate, WorkoutSessionRead, WorkoutSessionUpdate

CRUDWorkoutSession = FastCRUD[WorkoutSession, WorkoutSessionCreate, WorkoutSessionUpdate, WorkoutSessionUpdate, dict, WorkoutSessionRead]
crud_workout_session = CRUDWorkoutSession(WorkoutSession)

