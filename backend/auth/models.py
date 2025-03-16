
# Our request and response models:
from pydantic import BaseModel

# For saving user data to Firestore.
class UserDataRequest(BaseModel):
    email: str
    username: str

# For uploading a sprite to cloud storage.
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

# For chat requests using OpenAI API.
class ChatRequest(BaseModel):
    chat_context: str # Our context is a list of chat messages. Here, it's a JSON string.

# For image generation requests using DALL-E.
class ImageGenRequest(BaseModel):
    description: str