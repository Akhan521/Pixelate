
# Our gallery manager (implemented using Firebase).
import os
import sys
import json
import requests

# Adding the root directory to the Python path.
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

import pyrebase
from firebase_admin import firestore, storage
from backend.config import firebase_config
# from Pixelate.Firebase_Config.firebase_config import firebase_config

class GalleryManager:

    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.db = firestore.client()
        self.bucket = storage.bucket(name=firebase_config["storageBucket"])
        self.backend_url = self.auth_manager.backend_url

    # A method to upload a sprite to the gallery.
    def upload_sprite(self, title, description, file_name, pixels_data):
        '''
        Here is the structure of the pixels_data parameter:
            pixels_data: {
                "dimensions": (width, height),
                "pixels": { (x, y): rgba_tuple } 
            }
        '''
        try:
            
            # If the user is not logged in, return False.
            if not self.auth_manager.is_logged_in():
                return False
            
            user_id = self.auth_manager.get_user_id()
            
            # Send an upload request to the backend.
            response = requests.post(
                f"{self.backend_url}/sprite/upload",
                   json={
                        "title": title,
                        "description": description,
                        "creator_id": user_id,
                        "file_name": file_name,
                        "content": pixels_data
                    },
                    headers={"Authorization": f"Bearer {self.auth_manager.get_token()}"}
                )
            
            # If the request was successful, return True.
            if response.status_code == 200:
                return True
            return False
        
        except Exception as e:
            print(f"An error occurred while uploading sprite: {str(e)}")
            return False
        
    # A method to get our gallery of sprites.
    def get_gallery(self, limit=15):
        try:
            sprites = []
            # Retrieve the latest sprites from Firestore.
            query = self.db.collection("sprites").order_by("created_at", direction=firestore.Query.DESCENDING)
            query = query.limit(limit)
            results = query.stream()

            for doc in results:
                sprite = doc.to_dict()
                sprite["id"] = doc.id

                # Fetch the sprite creator's username.
                user = self.db.collection("users").document(sprite["creator_id"]).get()

                if user.exists:
                    user_data = user.to_dict()
                    sprite["creator_username"] = user_data.get("username", "Unknown")
                else:
                    sprite["creator_username"] = "Unknown"

                # Check if the current user has liked the sprite.
                sprite["liked_by_user"] = False
                # If the user is logged in, check if they have liked the sprite.
                if self.auth_manager.is_logged_in():
                    user_id = self.auth_manager.get_user_id()
                    like_ref = (
                        self.db.collection("likes")
                        .where("user_id", "==", user_id)
                        .where("sprite_id", "==", sprite["id"])
                        .limit(1)
                    )
                    likes = list(like_ref.stream())
                    if likes:
                        sprite["liked_by_user"] = True

                sprites.append(sprite)

            return sprites
        
        except Exception as e:
            print(f"An error occurred while fetching sprites: {e}")
            return []

    # A method to toggle the like status of a sprite.
    def toggle_like(self, sprite_id):
        try:
            user_id = self.auth_manager.get_user_id()
            # If the user is not logged in, return False.
            if not user_id:
                return False
            
            # Check if the user has already liked the sprite.
            like_ref = (
                self.db.collection("likes")
                .where("user_id", "==", user_id)
                .where("sprite_id", "==", sprite_id)
                .limit(1)
            )
            likes = list(like_ref.stream())

            # Storing the sprite reference.
            sprite_ref = self.db.collection("sprites").document(sprite_id)

            if likes:
                # Unlike the sprite - delete the like document + decrement the likes count.
                likes[0].reference.delete()
                sprite_ref.update({"likes": firestore.Increment(-1)})
                return ("Unliked", sprite_ref.get().to_dict())
            else:
                # Like the sprite - create a new like document + increment the likes count.
                like_data = {
                    "user_id": user_id,
                    "sprite_id": sprite_id,
                    "created_at": firestore.SERVER_TIMESTAMP
                }
                self.db.collection("likes").add(like_data)
                sprite_ref.update({"likes": firestore.Increment(1)})
                return ("Liked", sprite_ref.get().to_dict())
            
        except Exception as e:
            print(f"An error occurred while toggling like: {e}")
            return False
        
    # A method to get a sprite.
    def get_sprite(self, sprite_id):
        try:
            sprite_ref = self.db.collection("sprites").document(sprite_id)
            sprite = sprite_ref.get()

            # If the sprite does not exist, return None.
            if not sprite.exists:
                return None
            
            sprite_data = sprite.to_dict()
            sprite_data["id"] = sprite_id

            # Check if the current user has liked the sprite.
            sprite_data["liked_by_user"] = False
            # If the user is logged in, check if they have liked the sprite.
            if self.auth_manager.is_logged_in():
                user_id = self.auth_manager.get_user_id()
                like_ref = (
                    self.db.collection("likes")
                    .where("user_id", "==", user_id)
                    .where("sprite_id", "==", sprite_id)
                    .limit(1)
                )
                likes = list(like_ref.stream())
                if likes:
                    sprite_data["liked_by_user"] = True

            # Fetch the sprite creator's data.
            user = self.db.collection("users").document(sprite_data["creator_id"]).get()

            if user.exists:
                user_data = user.to_dict()
                sprite_data["creator_username"] = user_data.get("username", "Unknown")
            else:
                sprite_data["creator_username"] = "Unknown"

            # Download the sprite data from Firebase Storage.
            blob_path = sprite_data["storage_path"]
            blob = self.bucket.blob(blob_path)
            pixels_data_json = blob.download_as_string().decode("utf-8")
            pixels_data = json.loads(pixels_data_json)

            '''
            Here is the structure of pixels_data:
                pixels_data: {
                    "dimensions": [width, height],
                    "pixels": { 'x, y': [r, g, b, a] } # 'x, y' is a string.
                }

            We want it in this format:
                pixels_data: {
                    "dimensions": (width, height),
                    "pixels": { (x, y): (r, g, b, a) } # (x, y) is a tuple.
                }
            '''

            pixels_data = {
                "dimensions": tuple(pixels_data["dimensions"]),
                "pixels": {tuple(map(int, key.split(","))): tuple(value) for key, value in pixels_data["pixels"].items()}
            }

            sprite_data["pixels_data"] = pixels_data

            return sprite_data
        
        except Exception as e:
            print(f"An error occurred while fetching sprite: {e}")
            return None
