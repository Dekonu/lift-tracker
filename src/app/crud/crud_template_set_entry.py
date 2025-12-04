from fastcrud import FastCRUD

from ..models.template_set_entry import TemplateSetEntry
from ..schemas.template_set_entry import TemplateSetEntryCreate, TemplateSetEntryRead, TemplateSetEntryUpdate

CRUDTemplateSetEntry = FastCRUD[
    TemplateSetEntry,
    TemplateSetEntryCreate,
    TemplateSetEntryUpdate,
    TemplateSetEntryUpdate,
    dict,
    TemplateSetEntryRead,
]
crud_template_set_entry = CRUDTemplateSetEntry(TemplateSetEntry)

