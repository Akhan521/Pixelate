
# Our request and response models:
from pydantic import BaseModel

class LoginRequest(BaseModel):
    id_token: str # Provided by Firebase Client SDK.

class AuthResponse(BaseModel):
    user_id: str
    token: str    # Provided by Firebase Admin SDK.

# For saving user data to Firestore.
class UserDataRequest(BaseModel):
    email: str
    username: str

class SpriteUploadRequest(BaseModel):
    title: str
    description: str
    creator_id: str
    file_name: str
    content: dict # Our pixels data.