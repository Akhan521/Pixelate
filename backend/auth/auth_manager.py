
# Our authentication manager for user registration and login.
from firebase_admin import auth
from fastapi import HTTPException

class AuthManager:
        
    # A method to retrieve the current user's info. (Will be used as a dependency to verify the user's token.)
    def get_current_user(self, token: str) -> str:
        try:
            # Verify the provided ID token and return the user ID.
            decoded_token = auth.verify_id_token(token)
            user_id = decoded_token["uid"]
            return user_id
        
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid ID Token")