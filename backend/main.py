
# Our FASTAPI app for backend operations.
import os
import json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import Response
from auth.auth_manager import AuthManager
from auth.firestore_manager import FirestoreManager
from auth.storage_manager import StorageManager
from auth.models import (LoginRequest, AuthResponse, UserDataRequest, 
                         SpriteUploadRequest, ChatRequest, ImageGenRequest)
from firebase_admin import auth, firestore
from config import openai_api_key, dalle_api_key
from openai import OpenAI
import requests

# Initialize the FASTAPI app and other necessary components.
app = FastAPI()
security = HTTPBearer()
auth_manager = AuthManager()
firestore_manager = FirestoreManager()
storage_manager = StorageManager()
chat_client = OpenAI(
    api_key=openai_api_key,
)
dalle_client = OpenAI(
    api_key=dalle_api_key,
)

# Create a dependency to verify the user's ID token (for protected routes).
async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return auth_manager.get_current_user(token.credentials)

# Our save user data route to store user information in Firestore.
@app.post("/auth/save_user_data")
async def save_user_data(request: UserDataRequest, user_id: str = Depends(get_current_user)) -> dict:

    firestore_manager.save_user_data(user_id, request.email, request.username)
    return {"message": "User data saved successfully"}

# Our upload sprite route to store our .pix file to Firebase Storage and metadata to Firestore.
@app.post("/sprite/upload")
async def upload_sprite(request: SpriteUploadRequest, user_id: str = Depends(get_current_user)) -> dict:

    # Extract the request data and upload the sprite file to Firebase Storage.
    title = request.title
    description = request.description
    creator_id = request.creator_id
    file_name = request.file_name
    pixels_data = request.pixels_data # JSON string of sprite data.

    # If any of the required fields are missing, raise an HTTPException.
    if not all([title, description, creator_id, file_name, pixels_data]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # If the creator ID does not match the user ID, raise an HTTPException.
    if creator_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to upload sprite")
    
    # Save the sprite file to Firebase Storage.
    sprite_data = storage_manager.upload_sprite(user_id, title, description, file_name, pixels_data)
    return {"message": "Pix file uploaded successfully", "sprite_id": sprite_data["id"]}

# Our get gallery route to retrieve all sprites uploaded by users.
@app.get("/sprite/gallery")
async def get_gallery(limit: int = 15, user_id: str = Depends(get_current_user)) -> list[dict]:

    print("\nGetting gallery...\n")
    sprites = []
    # Retrieve the latest sprites from Firestore.
    query = firestore_manager.db.collection("sprites").order_by("created_at", direction=firestore.Query.DESCENDING)
    query = query.limit(limit)
    results = query.stream()

    print(f"\nResults = {results}\n")

    for doc in results:
        print(f"Sprite {doc.id} => {doc.to_dict()}")
        sprite = doc.to_dict()
        sprite["id"] = doc.id

        # Fetch the sprite creator's username.
        user = firestore_manager.db.collection("users").document(sprite["creator_id"]).get()

        if user.exists:
            user_data = user.to_dict()
            sprite["creator_username"] = user_data.get("username", "Unknown")
        else:
            sprite["creator_username"] = "Unknown"

        # Check if the current user has liked the sprite.
        sprite["liked_by_user"] = False
        if user_id:
            like_ref = (
                firestore_manager.db.collection("likes")
                .where("user_id", "==", user_id)
                .where("sprite_id", "==", sprite["id"])
                .limit(1)
            )
            likes = list(like_ref.stream())
            if likes:
                sprite["liked_by_user"] = True

        sprites.append(sprite)

    return sprites

# Our toggle like route to like or unlike a sprite.
@app.post("/sprite/{sprite_id}/toggle_like")
async def toggle_like(sprite_id: str, user_id: str = Depends(get_current_user)) -> dict:

    # Check if the user has already liked the sprite.
    like_ref = (
        firestore_manager.db.collection("likes")
        .where("user_id", "==", user_id)
        .where("sprite_id", "==", sprite_id)
        .limit(1)
    )
    likes = list(like_ref.stream())

    # Storing the sprite reference.
    sprite_ref = firestore_manager.db.collection("sprites").document(sprite_id)

    # If the sprite does not exist, raise an HTTPException.
    if not sprite_ref.get().exists:
        raise HTTPException(status_code=404, detail="Sprite not found")

    if likes:
        # Unlike the sprite - delete the like document + decrement the likes count.
        likes[0].reference.delete()
        sprite_ref.update({"likes": firestore.Increment(-1)})
        return {"action": "Unliked", "sprite": sprite_ref.get().to_dict()}
    else:
        # Like the sprite - create a new like document + increment the likes count.
        like_data = {
            "user_id": user_id,
            "sprite_id": sprite_id,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        firestore_manager.db.collection("likes").add(like_data)
        sprite_ref.update({"likes": firestore.Increment(1)})
        return {"action": "Liked", "sprite": sprite_ref.get().to_dict()}
    
# Our get sprite route to retrieve a specific sprite.
@app.get("/sprite/{sprite_id}")
async def get_sprite(sprite_id: str, user_id: str = Depends(get_current_user)) -> dict:

    sprite_ref = firestore_manager.db.collection("sprites").document(sprite_id)
    sprite = sprite_ref.get()

    # If the sprite does not exist, return an HTTPException.
    if not sprite.exists:
        raise HTTPException(status_code=404, detail="Sprite not found")
    
    sprite_data = sprite.to_dict()
    sprite_data["id"] = sprite_id

    # Check if the current user has liked the sprite.
    sprite_data["liked_by_user"] = False
    if user_id:
        like_ref = (
            firestore_manager.db.collection("likes")
            .where("user_id", "==", user_id)
            .where("sprite_id", "==", sprite_id)
            .limit(1)
        )
        likes = list(like_ref.stream())
        if likes:
            sprite_data["liked_by_user"] = True

    # Fetch the sprite creator's data.
    user = firestore_manager.db.collection("users").document(sprite_data["creator_id"]).get()

    if user.exists:
        user_data = user.to_dict()
        sprite_data["creator_username"] = user_data.get("username", "Unknown")
    else:
        sprite_data["creator_username"] = "Unknown"

    # Download the sprite data from Firebase Storage.
    blob_path = sprite_data["storage_path"]
    blob = storage_manager.bucket.blob(blob_path)
    pixels_data_json = blob.download_as_string().decode("utf-8")
    pixels_data = json.loads(pixels_data_json)

    '''
    Here is the structure of the pixels_data JSON string:
        pixels_data: {
            "dimensions": [width, height],
            "pixels": { 'x, y': [r, g, b, a] } # 'x, y' is a string.
        }
    '''

    sprite_data["pixels_data"] = pixels_data

    return sprite_data

# Our chat route to interact with our chatbot.
@app.post("/chat")
async def chat(request: ChatRequest) -> str:
    
    # Extract the chat context from the request.
    chat_context = request.chat_context
    chat_context = json.loads(chat_context)

    # If the chat context is empty, raise an HTTPException.
    if not chat_context:
        raise HTTPException(status_code=400, detail="Chat context is empty")
    
    try:
        # Send the entire chat context to our chatbot.
        response = chat_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_context
        )

        # Extract the chatbot's response.
        return response.choices[0].message.content
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while chatting: {str(e)}")
    
# Our image generation route to generate images using DALL-E.
@app.post("/image/generate")
async def generate_image(request: ImageGenRequest) -> Response:
    
    # Extract the image generation description from the request.
    description = request.description

    # If the description is empty, raise an HTTPException.
    if not description:
        raise HTTPException(status_code=400, detail="Description is empty")
    
    style_prompt = '''Style: A cartoonish, simple image with bold outlines and differentiable colors.'''
    
    try:
        # Generate an image using DALL-E.
        response = dalle_client.images.generate(
                model="dall-e-3",
                prompt=description + "\n" + style_prompt,
                n=1,
                size="1024x1024",
                quality="standard",
            )

        # If the response is successful, we'll store the image URL.
        if response and response.data and response.data[0].url:
            
            image_url = response.data[0].url
            
            # We'll download the image from the URL.
            image_data = requests.get(image_url).content

            # Return the image data in a response.
            return Response(content=image_data, media_type="image/png")
        
        else:
            raise HTTPException(status_code=500, detail="Failed to generate image")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while generating image: {str(e)}")

if __name__ == "__main__":
    # Run the FASTAPI app.
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.get("PORT", 8000)))