from fastcrud import FastCRUD

from ..models.user_profile import UserProfile
from ..schemas.user_profile import UserProfileCreate, UserProfileRead, UserProfileUpdate

CRUDUserProfile = FastCRUD[UserProfile, UserProfileCreate, UserProfileUpdate, UserProfileUpdate, dict, UserProfileRead]
crud_user_profile = CRUDUserProfile(UserProfile)
