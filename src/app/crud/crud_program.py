from fastcrud import FastCRUD

from ..models.program import Program
from ..schemas.program import ProgramCreate, ProgramRead, ProgramUpdate

CRUDProgram = FastCRUD[Program, ProgramCreate, ProgramUpdate, ProgramUpdate, dict, ProgramRead]
crud_program = CRUDProgram(Program)
