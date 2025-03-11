
# Our gallery manager (implemented using Firebase).
import os
import sys
import json
import requests

# Adding the root directory to the Python path.
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

class GalleryManager:

    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.backend_url = self.auth_manager.backend_url

    # A method to upload a sprite to the gallery.
    def upload_sprite(self, title, description, file_name, pixels_data):
        '''
        Here is the structure of the pixels_data parameter:
            pixels_data: {
                "dimensions": (width, height),
                "pixels": { (x, y): rgba_tuple } 
            }
        
        We want it in this format for the backend:
            pixels_data: {
                "dimensions": [width, height],
                "pixels": { 'x, y': [r, g, b, a] } 
            }
        '''
        try:
            
            # If the user is not logged in, return False.
            if not self.auth_manager.is_logged_in():
                return False
            
            user_id = self.auth_manager.get_user_id()

            # Convert the pixels_data to the format expected by the backend (Serializing to JSON).
            pixels_data = {
                "dimensions": list(pixels_data["dimensions"]),
                "pixels": {f"{x},{y}": list(rgba) for (x, y), rgba in pixels_data["pixels"].items()}
            }
            pixels_data = json.dumps(pixels_data)
            
            # Send an upload request to the backend.
            response = requests.post(
                f"{self.backend_url}/sprite/upload",
                   json={
                        "title": title,
                        "description": description,
                        "creator_id": user_id,
                        "file_name": file_name,
                        "pixels_data": pixels_data
                    },
                    headers={"Authorization": f"Bearer {self.auth_manager.get_token()}"}
                )
            
            # If the request was successful, return True.
            if response.status_code == 200:
                return True
            return False
        
        except requests.exceptions.RequestException as e:
            error_msg = e.response.json().get("detail", str(e)) if hasattr(e, "response") else str(e)
            print(f"An error occurred while uploading sprite: {error_msg}")
            print(f"Full response: {e.response.text if hasattr(e, 'response') else 'No response'}")
            print(f"Status code: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
            return False
        
    # A method to get our gallery of sprites.
    def get_gallery(self, limit=15):
        try:
            headers = {}
            # If the user is logged in, send the token in the request headers.
            if self.auth_manager.is_logged_in():
                headers["Authorization"] = f"Bearer {self.auth_manager.get_token()}"

            # Send a request to the backend to fetch the gallery.
            response = requests.get(
                f"{self.backend_url}/sprite/gallery",
                params={"limit": limit},
                headers=headers
            )

            # If the request was successful, return the sprites.
            if response.status_code == 200:
                return response.json()
            return []

        except requests.exceptions.RequestException as e:
            error_msg = e.response.json().get("detail", str(e)) if hasattr(e, "response") else str(e)
            print(f"An error occurred while fetching sprites: {error_msg}")
            return []

    # A method to toggle the like status of a sprite.
    def toggle_like(self, sprite_id):
        try:
            
            # If the user is not logged in, return False.
            if not self.auth_manager.is_logged_in():
                return False
            
            user_id = self.auth_manager.get_user_id()

            # Send a toggle like request to the backend.
            response = requests.post(
                f"{self.backend_url}/sprite/{sprite_id}/toggle_like",
                headers={"Authorization": f"Bearer {self.auth_manager.get_token()}"}
            )

            # If the request was successful, return the like status and updated sprite data.
            if response.status_code == 200:
                like_data = response.json()
                return (like_data["action"], like_data["sprite"])
            return (False, None)
        
        except requests.exceptions.RequestException as e:
            error_msg = e.response.json().get("detail", str(e)) if hasattr(e, "response") else str(e)
            print(f"An error occurred while toggling like: {error_msg}")
            return (False, None)
        
    # A method to get a sprite.
    def get_sprite(self, sprite_id):
        try:
            headers = {}
            # If the user is logged in, send the token in the request headers.
            if self.auth_manager.is_logged_in():
                headers["Authorization"] = f"Bearer {self.auth_manager.get_token()}"

            # Send a request to the backend to fetch the sprite.
            response = requests.get(
                f"{self.backend_url}/sprite/{sprite_id}",
                headers=headers
            )

            # If the request was successful, return the sprite.
            if response.status_code == 200:
                return response.json()
            return None

        except requests.exceptions.RequestException as e:
            error_msg = e.response.json().get("detail", str(e)) if hasattr(e, "response") else str(e)
            print(f"An error occurred while fetching sprite: {error_msg}")
            return None
