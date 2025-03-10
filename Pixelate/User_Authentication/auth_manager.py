
# Our user authentication manager (implemented using Firebase).
import os
import sys

# Adding the root directory to the Python path.
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

import pyrebase
from firebase_admin import firestore
from backend.config import firebase_config
from PyQt6.QtCore import QObject
import requests
import json

class AuthManager(QObject):

    def __init__(self):
        super().__init__()
        self.backend_url = "http://localhost:8000"

        # Firebase client configuration.
        self.firebase = pyrebase.initialize_app(firebase_config)
        self.auth = self.firebase.auth()
        self.db = firestore.client()
        self.user = None
        self.token = None

    def register(self, email: str, password: str, username: str) -> tuple[bool, str]:
        try:
            # Create a new user with the specified email and password.
            user = self.auth.create_user_with_email_and_password(email, password)
            id_token = user["idToken"]

            # Send the ID token to the backend for verification.
            response = requests.post(f"{self.backend_url}/auth/login", json={"id_token": id_token})

            # If the request was successful, we'll extract the user ID and custom token.
            if response.status_code == 200:
                user_info = response.json()
                self.user = user
                self.token = user_info["token"] # Custom token for backend operations.
                return (True, None)
            
            else:
                error = response.json()
                error_msg = error["detail"]
                print(f"An error occurred while registering: {error_msg}")
                return (False, error_msg)
        
        except requests.exceptions.HTTPError as e:
            # If an error occurred, we'll extract the error message from the response.
            error_response = e.args[1]
            error = json.loads(error_response)
            error_msg = error["error"]["message"]
            print(f"An error occurred while registering: {error_msg}")
            return (False, error_msg)
        
        except Exception as e:
            print(f"An error occurred while registering: {str(e)}")
            return (False, str(e))
        
    def login(self, email: str, password: str) -> tuple[bool, str]:
        try:
            # Attempt to sign in using Firebase Client SDK.
            user = self.auth.sign_in_with_email_and_password(email, password)
            id_token = user["idToken"]
            
            # Send the ID token to the backend for verification.
            response = requests.post(f"{self.backend_url}/auth/login", json={"id_token": id_token})

            # If the request was successful, we'll extract the user ID and custom token.
            if response.status_code == 200:
                user_info = response.json()
                self.user = user
                self.token = user_info["token"] # Custom token for backend operations.
                return (True, None)
            else:
                error = response.json()
                error_msg = error["detail"]
                print(f"An error occurred while logging in: {error_msg}")
                return (False, error_msg)
        
        except requests.exceptions.HTTPError as e:
            # If an error occurred, we'll extract the error message from the response.
            error_response = e.args[1]
            error = json.loads(error_response)
            error_msg = error["error"]["message"]
            print(f"An error occurred while logging in: {error_msg}")
            return (False, error_msg)
        
        except Exception as e:
            print(f"An error occurred while logging in: {str(e)}")
            return (False, str(e))
        
    def logout(self):
        self.user = None

    def get_user_id(self):
        if self.user:
            return self.user["localId"]
        return None
    
    def get_token(self):
        return self.token

    def is_logged_in(self):
        return self.user is not None and self.token is not None