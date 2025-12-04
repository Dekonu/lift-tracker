from fastcrud import FastCRUD

from ..models.scheduled_workout import ScheduledWorkout
from ..schemas.scheduled_workout import (
    ScheduledWorkoutCreate,
    ScheduledWorkoutRead,
    ScheduledWorkoutUpdate,
)

CRUDScheduledWorkout = FastCRUD[
    ScheduledWorkout,
    ScheduledWorkoutCreate,
    ScheduledWorkoutUpdate,
    ScheduledWorkoutUpdate,
    dict,
    ScheduledWorkoutRead,
]
crud_scheduled_workout = CRUDScheduledWorkout(ScheduledWorkout)
