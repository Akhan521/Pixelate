
# Our Firebase configuration for backend operations.
import os
import sys
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Load the environment variables.
load_dotenv()

# Initialize Pyrebase for frontend operations.
firebase_config = {
    "apiKey": "AIzaSyAOiScyR37CTeaoMbUcl-PWKCaZrVqL9JY",
    "authDomain": "pixelate-c1517.firebaseapp.com",
    "projectId": "pixelate-c1517",
    "storageBucket": "pixelate-c1517.firebasestorage.app",
    "messagingSenderId": "259940749903",
    "appId": "1:259940749903:web:d6fe2921707d5395b9d03a",
    "measurementId": "G-K8M4NC53R1",
    "databaseURL": ""
}

# Initialize the Firebase Admin SDK for backend operations.
cred = credentials.Certificate(f"{os.path.dirname(__file__)}/{os.getenv('FIREBASE_ADMIN_SDK')}")
firebase_admin.initialize_app(cred, {
    "storageBucket": "pixelate-c1517.firebasestorage.app"
})