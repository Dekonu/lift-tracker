from fastcrud import FastCRUD

from ..models.sharing_permission import SharingPermission
from ..schemas.sharing_permission import SharingPermissionCreate, SharingPermissionRead, SharingPermissionUpdate

CRUDSharingPermission = FastCRUD[SharingPermission, SharingPermissionCreate, SharingPermissionUpdate, SharingPermissionUpdate, dict, SharingPermissionRead]
crud_sharing_permission = CRUDSharingPermission(SharingPermission)

