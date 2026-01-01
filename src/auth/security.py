import bcrypt
from src.database.crud import get_user_by_email as db_get_user, update_password

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def get_user_by_email(email: str):
    return db_get_user(email)

def change_password(email: str, current_pass: str, new_pass: str) -> bool:
    """
    Verifies current password and updates to new password.
    Returns True if successful, False otherwise.
    """
    user = db_get_user(email)
    if not user:
        return False
    
    # User schema assumption: (id, email, password_hash, ...)
    # verify_password expects (plain, hashed)
    stored_hash = user[2] 
    
    if verify_password(current_pass, stored_hash):
        new_hash = hash_password(new_pass)
        return update_password(user[0], new_hash)
        
    return False
