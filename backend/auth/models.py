
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
    pixels_data: str # JSON string of sprite data.

    '''
    Here is the structure of the pixels_data JSON string:
        pixels_data: {
            "dimensions": [width, height],
            "pixels": { 'x, y': [r, g, b, a]
        }
    '''

class ChatRequest(BaseModel):
    chat_context: str # Our context is a list of chat messages. Here, it's a JSON string.

class ImageGenRequest(BaseModel):
    description: str