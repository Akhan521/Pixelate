
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

class AuthManager:

    def __init__(self):
        self.firebase = pyrebase.initialize_app(firebase_config)
        self.auth = self.firebase.auth()
        self.db = firestore.client()
        self.user = None

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
            return True
        
        except Exception as e:
            print(f"An error occurred while registering: {e}")
            return False
        
    def login(self, email, password):
        try:
            # Sign in the user with the specified email and password.
            user = self.auth.sign_in_with_email_and_password(email, password)
            self.user = user
            return True
        
        except Exception as e:
            print(f"An error occurred while logging in: {e}")
            return False
        
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
    