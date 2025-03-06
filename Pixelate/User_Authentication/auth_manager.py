
# Our user authentication manager (implemented using Firebase).
import os
import sys

# Adding the root directory to the Python path.
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

import pyrebase
from firebase_admin import firestore
from Pixelate.Firebase_Config.firebase_config import firebase_config
import requests
import json

class AuthManager:

    def __init__(self):
        self.firebase = pyrebase.initialize_app(firebase_config)
        self.auth = self.firebase.auth()
        self.db = firestore.client()
        # For testing purposes, we'll sign in with a test account.
        self.user = self.auth.sign_in_with_email_and_password("darth@mail.com", "darthvader")
        # self.user = None

    def register(self, email, password, username):
        try:
            # Create a new user with the specified email and password.
            self.user = self.auth.create_user_with_email_and_password(email, password)

            # Next, we'll store some additional user information in Firestore.
            user_data = {
                "email": email,
                "username": username,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            self.db.collection("users").document(self.get_user_id()).set(user_data)
            return (True, None)
        
        except requests.exceptions.HTTPError as e:
            # If an error occurred, we'll extract the error message from the response.
            error_response = e.args[1]
            error = json.loads(error_response)
            error_msg = error["error"]["message"]
            print(f"An error occurred while registering: {error_msg}")
            return (False, error_msg)
        
        except Exception as e:
            print(f"An error occurred while registering: {e}")
            return (False, e)
        
    def login(self, email, password):
        try:
            # Sign in the user with the specified email and password.
            user = self.auth.sign_in_with_email_and_password(email, password)
            self.user = user
            return (True, None)
        
        except requests.exceptions.HTTPError as e:
            # If an error occurred, we'll extract the error message from the response.
            error_response = e.args[1]
            error = json.loads(error_response)
            error_msg = error["error"]["message"]
            print(f"An error occurred while logging in: {error_msg}")
            return (False, error_msg)
        
        except Exception as e:
            print(f"An error occurred while logging in: {e}")
            return (False, e)
        
    def logout(self):
        self.user = None

    def get_user_id(self):
        if self.user:
            return self.user["localId"]
        return None
    
    def get_user_data(self):
        if self.user:
            user_data = self.db.collection("users").document(self.get_user_id()).get()
            return user_data.to_dict()
        return None
    
    def is_logged_in(self):
        return self.user is not None