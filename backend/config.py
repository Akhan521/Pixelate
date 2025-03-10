
# Our Firebase configuration for backend operations.
import os
import sys
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Load the environment variables.
load_dotenv()

# Retrieving our service account key from Render.
if "FIREBASE_SERVICE_ACCOUNT" in os.environ:
    # Load the service account key from the environment variable.
    service_account_json = os.environ["FIREBASE_SERVICE_ACCOUNT"]
    cred = credentials.Certificate(json.loads(service_account_json))
    firebase_admin.initialize_app(cred, {
        "storageBucket": "pixelate-c1517.firebasestorage.app"
    })
else:
    raise ValueError("The FIREBASE_SERVICE_ACCOUNT environment variable was not found.")
