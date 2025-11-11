from fastcrud import FastCRUD

from ..models.set import Set
from ..schemas.set import SetCreate, SetRead, SetUpdate

CRUDSet = FastCRUD[Set, SetCreate, SetUpdate, SetUpdate, dict, SetRead]
crud_sets = CRUDSet(Set)

