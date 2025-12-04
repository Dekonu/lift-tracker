from fastcrud import FastCRUD

from ..models.one_rm import OneRM
from ..schemas.one_rm import OneRMCreate, OneRMRead, OneRMUpdate

CRUDOneRM = FastCRUD[OneRM, OneRMCreate, OneRMUpdate, OneRMUpdate, dict, OneRMRead]
crud_one_rm = CRUDOneRM(OneRM)
