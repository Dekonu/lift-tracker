from fastcrud import FastCRUD

from ..models.set_entry import SetEntry
from ..schemas.set_entry import SetEntryCreate, SetEntryRead, SetEntryUpdate

CRUDSetEntry = FastCRUD[SetEntry, SetEntryCreate, SetEntryUpdate, SetEntryUpdate, dict, SetEntryRead]
crud_set_entry = CRUDSetEntry(SetEntry)
