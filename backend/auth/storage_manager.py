
# Our cloud storage manager for .pix file uploads.
from firebase_admin import storage, firestore
from fastapi import HTTPException
import json

class StorageManager:

    def __init__(self):
        self.bucket = storage.bucket()
        self.db = firestore.client()

    # A method to upload a .pix file to Firebase Storage + store sprite metadata in Firestore.
    def upload_pix_file(self, title: str, description: str, file_name: str, pixels_data: str) -> bool:
        pass