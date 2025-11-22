from datetime import datetime

from pydantic import BaseModel

from ..models.user_relationship import RelationshipType


class UserRelationshipBase(BaseModel):
    related_user_id: int
    relationship_type: RelationshipType


class UserRelationshipCreate(UserRelationshipBase):
    user_id: int


class UserRelationshipUpdate(BaseModel):
    relationship_type: RelationshipType | None = None


class UserRelationshipRead(UserRelationshipBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None

