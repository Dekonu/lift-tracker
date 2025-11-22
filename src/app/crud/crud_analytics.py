from fastcrud import FastCRUD

from ..models.analytics import StrengthProgression, VolumeTracking
from ..schemas.analytics import (
    StrengthProgressionCreate,
    StrengthProgressionRead,
    VolumeTrackingCreate,
    VolumeTrackingRead,
)

CRUDVolumeTracking = FastCRUD[VolumeTracking, VolumeTrackingCreate, dict, dict, dict, VolumeTrackingRead]
crud_volume_tracking = CRUDVolumeTracking(VolumeTracking)

CRUDStrengthProgression = FastCRUD[StrengthProgression, StrengthProgressionCreate, dict, dict, dict, StrengthProgressionRead]
crud_strength_progression = CRUDStrengthProgression(StrengthProgression)

