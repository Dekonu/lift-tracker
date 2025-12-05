from fastcrud import FastCRUD

from ..models.program_day_assignment import ProgramDayAssignment
from ..schemas.program_day_assignment import (
    ProgramDayAssignmentCreate,
    ProgramDayAssignmentRead,
    ProgramDayAssignmentUpdate,
)

CRUDProgramDayAssignment = FastCRUD[
    ProgramDayAssignment,
    ProgramDayAssignmentCreate,
    ProgramDayAssignmentUpdate,
    ProgramDayAssignmentUpdate,
    dict,
    ProgramDayAssignmentRead,
]
crud_program_day_assignment = CRUDProgramDayAssignment(ProgramDayAssignment)

