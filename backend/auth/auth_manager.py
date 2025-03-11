
# Our authentication manager for user registration and login.
from firebase_admin import auth
from fastapi import HTTPException

class AuthManager:

    # A method to verify the ID token provided by Firebase Client SDK.
    def verify_token(self, id_token: str) -> dict:
        try:
            # Verify the ID token and extract the user ID.
            decoded_token = auth.verify_id_token(id_token)
            user_id = decoded_token["uid"]

            # Generate a custom token for the user (for backend operations).
            custom_token = auth.create_custom_token(user_id)
            return {"user_id": user_id, "token": custom_token.decode()}
        
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid ID token")
        
    # A method to retrieve the current user's info. (Will be used as a dependency to verify the user's custom token.)
    def get_current_user(self, custom_token: str) -> str:
        try:
            # Verify the provided custom token and return the user ID.
            decoded_token = auth.verify_custom_token(custom_token)
            return decoded_token["uid"]
        
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired custom token")