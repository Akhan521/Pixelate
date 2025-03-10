
# Our request and response models for user authentication.
from pydantic import BaseModel
from firebase_admin import firestore

class LoginRequest(BaseModel):
    id_token: str # Provided by Firebase Client SDK.

class AuthResponse(BaseModel):
    user_id: str
    token: str    # Provided by Firebase Admin SDK.

class UserDataRequest(BaseModel):
    email: str
    username: str = None # Provided when the user registers.
    created_at: firestore.SERVER_TIMESTAMP

class PixFileRequest(BaseModel):
    file_name: str
    content: str  # .pix file content as a string.