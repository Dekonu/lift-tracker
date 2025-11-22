from fastcrud import FastCRUD

from ..models.program_week import ProgramWeek
from ..schemas.program_week import ProgramWeekCreate, ProgramWeekRead, ProgramWeekUpdate

CRUDProgramWeek = FastCRUD[ProgramWeek, ProgramWeekCreate, ProgramWeekUpdate, ProgramWeekUpdate, dict, ProgramWeekRead]
crud_program_week = CRUDProgramWeek(ProgramWeek)

