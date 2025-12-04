from fastcrud import FastCRUD

from ..models.user_relationship import UserRelationship
from ..schemas.user_relationship import UserRelationshipCreate, UserRelationshipRead, UserRelationshipUpdate

CRUDUserRelationship = FastCRUD[
    UserRelationship, UserRelationshipCreate, UserRelationshipUpdate, UserRelationshipUpdate, dict, UserRelationshipRead
]
crud_user_relationship = CRUDUserRelationship(UserRelationship)
