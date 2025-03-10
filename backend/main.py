
# Our FASTAPI app for backend operations.
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.auth_manager import AuthManager
from auth.firestore_manager import FirestoreManager
from auth.storage_manager import StorageManager
from auth.models import LoginRequest, AuthResponse, UserDataRequest, SpriteUploadRequest
from config import firebase_admin

# Initialize the FASTAPI app and other necessary components.
app = FastAPI()
security = HTTPBearer()
auth_manager = AuthManager()
firestore_manager = FirestoreManager()
storage_manager = StorageManager()

# Create a dependency to verify the user's custom token (for protected routes).
async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return auth_manager.get_current_user(token.credentials)

# Our login route to authenticate the user.
@app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    
    # Verify the ID token provided by the Firebase Client SDK.
    user_info = auth_manager.verify_token(request.id_token)
    
    # Return the user's ID and custom token for backend operations.
    return AuthResponse(user_id=user_info["user_id"], token=user_info["token"])

# Our save user data route to store user information in Firestore.
@app.post("/auth/save_user_data")
async def save_user_data(request: UserDataRequest, user_id: str = Depends(get_current_user)) -> dict:

    firestore_manager.save_user_data(user_id, request.email, request.username)
    return {"message": "User data saved successfully"}

# Our upload sprite route to store our .pix file to Firebase Storage and metadata to Firestore.
@app.post("/sprite/upload")
async def upload_sprite(request: SpriteUploadRequest, user_id: str = Depends(get_current_user)) -> dict:

    sprite_data = storage_manager.upload_sprite(user_id, request.title, request.description, request.file_name, request.content)
    return {"message": "Pix file uploaded successfully", "sprite_id": sprite_data["id"]}

if __name__ == "__main__":
    # Run the FASTAPI app.
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.get("PORT", 8000)))