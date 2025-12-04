from fastcrud import FastCRUD

from ..models.muscle_group import MuscleGroup
from ..schemas.muscle_group import MuscleGroupCreate, MuscleGroupRead, MuscleGroupUpdate

CRUDMuscleGroup = FastCRUD[
    MuscleGroup,
    MuscleGroupCreate,
    MuscleGroupUpdate,
    MuscleGroupUpdate,
    dict,
    MuscleGroupRead,
]
crud_muscle_groups = CRUDMuscleGroup(MuscleGroup)
