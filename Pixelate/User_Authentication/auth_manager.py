
# Our user authentication manager (implemented using Firebase).
import os
import sys
import time

# Adding the root directory to the Python path.
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

import pyrebase
from firebase_config import firebase_config
from PyQt6.QtCore import QObject
import requests
import json

class AuthManager(QObject):

    def __init__(self):
        super().__init__()
        self.backend_url = "https://pixelate-backend.onrender.com"

        # Firebase client configuration.
        self.firebase = pyrebase.initialize_app(firebase_config)
        self.auth = self.firebase.auth()
        self.user = None
        self.token = None
        self.user_id = None   # Backend authenticated user ID.
        self.token_expiry = 0 # Token expiration time (for refreshing).

    def register(self, email: str, password: str, username: str) -> tuple[bool, str]:
        try:
            # Create a new user with the specified email and password.
            user = self.auth.create_user_with_email_and_password(email, password)
            id_token = user["idToken"]

            # Send the ID token to the backend for verification.
            response = requests.post(f"{self.backend_url}/auth/login", json={"id_token": id_token})

            # If the request was successful, we'll extract the user ID and token.
            if response.status_code == 200:
                user_info = response.json()
                self.user = user
                self.token = user_info["token"] 
                self.user_id = user_info["user_id"]
                self.token_expiry = int(time.time()) + 3600 # Set token to expire in 1 hour.
                return (True, None)
            
            else:
                error_msg = response.json().get("detail", str(response.json()))
                print(f"An error occurred while registering: {error_msg}")
                return (False, error_msg)
        
        except requests.exceptions.HTTPError as e:
            # If an error occurred, we'll extract the error message from the response.
            error_response = e.args[1]
            error = json.loads(error_response)
            error_msg = error["error"]["message"]
            print(f"An error occurred while logging in: {error_msg}")
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

            # If the request was successful, we'll extract the user ID and token.
            if response.status_code == 200:
                user_info = response.json()
                self.user = user
                self.token = user_info["token"] 
                self.user_id = user_info["user_id"]
                self.token_expiry = int(time.time()) + 3600 # Set token to expire in 1 hour.
                return (True, None)
            else:
                error_msg = response.json().get("detail", str(response.json()))
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
        self.token = None
        self.user_id = None
        self.token_expiry = 0

    # If our token has expired or is about to expire, we'll refresh it.
    def refresh_token(self):
        if not self.is_logged_in():
            return False
        
        current_time = int(time.time())
        five_minutes = 300

        if self.token_expiry - current_time <= five_minutes:
            try:
                print("Refreshing token...")
                # Refresh the user's token using their refresh token.
                refreshed_user = self.auth.refresh(self.user["refreshToken"])
                id_token = refreshed_user["idToken"]
                self.user = refreshed_user

                # Send the new ID token to the backend for verification and generate a new token.
                response = requests.post(f"{self.backend_url}/auth/login", json={"id_token": id_token})

                # If the request was successful, we'll extract the user ID and token.
                if response.status_code == 200:
                    user_info = response.json()
                    self.token = user_info["token"]
                    self.user_id = user_info["user_id"]
                    self.token_expiry = int(time.time()) + 3600 # Set token to expire in 1 hour.
                    print(f"Token refreshed successfully. New expiry: {self.token_expiry}")
                    return True
                else:
                    error = response.json()
                    error_msg = error["detail"]
                    print(f"An error occurred while refreshing token: {error_msg}")
                    self.logout()
                    return False
                
            except Exception as e:
                print(f"An error occurred while refreshing token: {str(e)}")
                self.logout()
                return False

        return True
                
    def get_user_id(self):
        return self.user_id
    
    def get_token(self):
        
        # If the token is about to expire, we'll refresh it. If the refresh fails, we'll return None.
        if not self.refresh_token():
            return None
        
        return self.token

    def is_logged_in(self):
        return self.user is not None and self.token is not None and self.user_id is not None