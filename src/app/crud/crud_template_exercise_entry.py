from fastcrud import FastCRUD

from ..models.template_exercise_entry import TemplateExerciseEntry
from ..schemas.template_exercise_entry import (
    TemplateExerciseEntryCreate,
    TemplateExerciseEntryRead,
    TemplateExerciseEntryUpdate,
)

CRUDTemplateExerciseEntry = FastCRUD[
    TemplateExerciseEntry,
    TemplateExerciseEntryCreate,
    TemplateExerciseEntryUpdate,
    TemplateExerciseEntryUpdate,
    dict,
    TemplateExerciseEntryRead,
]
crud_template_exercise_entry = CRUDTemplateExerciseEntry(TemplateExerciseEntry)

