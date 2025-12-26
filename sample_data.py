from src.database.schema import init_db
from src.database.crud import create_user, add_transaction, get_user_by_username
from src.auth.security import hash_password
from datetime import datetime, timedelta
import random

def generate_sample_data():
    # 1. Initialize DB
    init_db()
    
    # 2. Create Test User
    username = "testuser"
    password = "password123"
    
    if not get_user_by_username(username):
        pwd_hash = hash_password(password)
        user_id = create_user(username, pwd_hash, "Test User")
        print(f"User '{username}' created.")
    else:
        user = get_user_by_username(username)
        user_id = user['id']
        print(f"User '{username}' already exists.")

    # 3. Add Sample Expenses
    categories = ["Food & Dining", "Transportation", "Shopping", "Utilities", "Entertainment", "Health"]
    methods = ["Cash", "Debit Card", "Credit Card", "UPI"]
    notes = ["Lunch", "Grocery", "Uber", "Bill", "Cinema", "Pharmacy", "Gift", "New Shoes"]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    print("Generating 100 sample expenses...")
    count = 0
    for _ in range(100):
        # Weighted random amount
        amount = round(random.uniform(50, 2000), 2)
        if random.random() < 0.1: amount *= 5 # Occasionally large expense
        
        # Random date
        days_diff = random.randint(0, 90)
        date = (start_date + timedelta(days=days_diff)).date()
        
        cat = random.choice(categories)
        meth = random.choice(methods)
        note = random.choice(notes)
        
        if add_transaction(user_id, amount, cat, meth, date, note):
            count += 1
            
    print(f"Successfully added {count} sample expenses for '{username}'.")
    print("---")
    print("Login Credentials:")
    print(f"Username: {username}")
    print(f"Password: {password}")

if __name__ == "__main__":
    generate_sample_data()
