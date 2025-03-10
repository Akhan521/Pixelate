
# Our firestore manager to handle database operations.
from firebase_admin import firestore
from fastapi import HTTPException

class FirestoreManager:

    def __init__(self):
        self.db = firestore.client()

    # A method to save user data to Firestore.
    def save_user_data(self, user_id: str, email: str, username: str = None) -> None:
        try:
            # Store data in the 'users' collection.
            user_data = {
                "email": email,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            if username:
                user_data["username"] = username
            self.db.collection("users").document(user_id).set(user_data, merge=True)
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while saving user data: {str(e)}")
        
    # A method to retrieve user data from Firestore.
    def get_user_data(self, user_id: str) -> dict:
        try:
            # Retrieve the user's data from Firestore.
            user_data = self.db.collection("users").document(user_id).get()
            if user_data.exists:
                return user_data.to_dict()
            return {}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while retrieving user data: {str(e)}")