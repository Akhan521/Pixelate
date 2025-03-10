
# Our request and response models for user authentication.
from pydantic import BaseModel
from pydantic.config import ConfigDict
from firebase_admin import firestore

class LoginRequest(BaseModel):
    id_token: str # Provided by Firebase Client SDK.

class AuthResponse(BaseModel):
    user_id: str
    token: str    # Provided by Firebase Admin SDK.

class UserDataRequest(BaseModel):
    email: str
    username: str = None # Provided when the user registers.
    created_at: firestore.SERVER_TIMESTAMP = firestore.SERVER_TIMESTAMP

    # To allow for firestore timestamps:
    model_config = ConfigDict(arbitrary_types_allowed=True) 

class SpriteUploadRequest(BaseModel):
    title: str
    description: str
    creator_id: str
    file_name: str
    content: str   # .pix file content as a string.