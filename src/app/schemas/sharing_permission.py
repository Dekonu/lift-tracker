from datetime import datetime

from pydantic import BaseModel

from ..models.sharing_permission import ShareableResourceType


class SharingPermissionBase(BaseModel):
    resource_type: ShareableResourceType
    resource_id: int
    shared_with_user_id: int | None = None  # None = public
    can_view: bool = True
    can_edit: bool = False
    can_copy: bool = True


class SharingPermissionCreate(SharingPermissionBase):
    owner_user_id: int


class SharingPermissionUpdate(BaseModel):
    can_view: bool | None = None
    can_edit: bool | None = None
    can_copy: bool | None = None


class SharingPermissionRead(SharingPermissionBase):
    id: int
    owner_user_id: int
    created_at: datetime
    updated_at: datetime | None
