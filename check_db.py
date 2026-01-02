import sqlite3
import os

DB_PATH = "finance_pro.db"

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} does not exist.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check users table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
    schema = cursor.fetchone()
    if schema:
        print("--- Current 'users' table schema ---")
        sql = schema[0]
        print(sql)
        if "NOT NULL" in sql.split("email")[1].split(",")[0]:
            print("RESULT: email is still NOT NULL ❌")
        else:
            print("RESULT: email is now NULLABLE ✅")
    else:
        print("'users' table not found.")
    
    # Check actual data for any integrity issues
    cursor.execute("SELECT id, username, email FROM users LIMIT 5")
    rows = cursor.fetchall()
    print("\n--- Data Sample (ID, Username, Email) ---")
    for row in rows:
        print(row)
        
    conn.close()

if __name__ == "__main__":
    check_schema()
