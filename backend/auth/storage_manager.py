
# Our cloud storage manager for .pix file uploads.
from firebase_admin import storage, firestore
from fastapi import HTTPException
import json

class StorageManager:

    def __init__(self):
        self.bucket = storage.bucket()
        self.db = firestore.client()

    # A method to upload a .pix file to Firebase Storage + store sprite metadata in Firestore.
    def upload_sprite(self, user_id: str, title: str, description: str, file_name: str, pixels_data: dict) -> dict:
        
        try:
            # Create a new document in the "sprites" collection.
            sprite_ref = self.db.collection("sprites").document()
            sprite_id = sprite_ref.id

            # Set up the blob path (storage path) for the sprite.
            blob_path = f"sprites/{user_id}/{file_name}"
            blob = self.bucket.blob(blob_path)
            
            # Prepare the sprite data for upload (serializing to JSON).
            sprite_data = {
                "dimensions": list(pixels_data["dimensions"]),
                "pixels": {f"{x},{y}": list(rgba) for (x, y), rgba in pixels_data["pixels"].items()}
            }
            sprite_data_json = json.dumps(sprite_data)

            # Upload the sprite data to Firebase Storage.
            blob.upload_from_string(sprite_data_json, content_type="application/json")

            # Make the sprite publicly accessible.
            blob.make_public()

            # Store the sprite metadata in Firestore.
            sprite_data = {
                "title": title,
                "description": description,
                "creator_id": user_id,
                "storage_path": blob_path,
                "public_url": blob.public_url,
                "created_at": firestore.SERVER_TIMESTAMP,
                "likes": 0
            }
            sprite_ref.set(sprite_data)
            return {"id": sprite_id, **sprite_data}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while uploading the sprite: {str(e)}")