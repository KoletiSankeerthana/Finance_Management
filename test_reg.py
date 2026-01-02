import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.database.crud import create_user
from src.auth.security import hash_password

def test_registration():
    username = "testuser_unique_123"
    password = "testpassword"
    pwd_hash = hash_password(password)
    
    print(f"Attempting to create user: {username}")
    user_id = create_user(username, pwd_hash)
    
    if user_id:
        print(f"SUCCESS: User created with ID {user_id}")
    else:
        print("FAILURE: Could not create user.")

if __name__ == "__main__":
    test_registration()
