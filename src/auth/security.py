import bcrypt
from src.database.crud import get_user_by_username as db_get_user_username, update_password

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    if not password or not hashed:
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except (ValueError, AttributeError):
        return False

def get_user_by_username(username: str):
    return db_get_user_username(username)

def change_password(username: str, current_pass: str, new_pass: str) -> bool:
    """
    Verifies current password and updates to new password.
    Returns True if successful, False otherwise.
    """
    user = db_get_user_username(username)
    if not user:
        return False
    
    # User schema: (id, username, email, password_hash, ...)
    stored_hash = user['password_hash'] if isinstance(user, dict) else user[3]
    
    if verify_password(current_pass, stored_hash):
        new_hash = hash_password(new_pass)
        user_id = user['id'] if isinstance(user, dict) else user[0]
        return update_password(user_id, new_hash)
        
    return False
