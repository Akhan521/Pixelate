
# Our request and response models:
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from typing import Dict, List

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
    pixels_data: Dict[str, any] = Field(
        ...,
        description="A dictionary containing the sprite's pixel data.",
        example = {
            "dimensions": [16, 16],
            "pixels": {
                "0,0": [255, 255, 255, 255],
                "0,1": [255, 255, 255, 255],
                "0,2": [255, 255, 255, 255],
                "0,3": [255, 255, 255, 255],
            }
        }
    )

    # To allow for the 'any' type, we need to override the Config class.
    class Config:
        arbitrary_types_allowed = True