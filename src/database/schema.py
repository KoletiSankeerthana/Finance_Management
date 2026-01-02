import sqlite3
import os

DB_PATH = "finance_pro.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrency and sync on cloud servers
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users Table (V33: Added username field)
    try:
        cursor.execute("SELECT username FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # Migration: Add username column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
            # Set default usernames for existing users (email prefix)
            cursor.execute("""
                UPDATE users 
                SET username = SUBSTR(email, 1, INSTR(email, '@') - 1)
                WHERE username IS NULL
            """)
        except sqlite3.OperationalError:
            pass  # Column might already exist
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Categories Table (V3: Emoji support, no color)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        emoji TEXT DEFAULT '🏷️',
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # Transactions Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        payment_method TEXT NOT NULL,
        date DATE NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # Budgets Table (V41: Supporting Weekly, Monthly & Custom)
    try:
        # Instead of dropping, we can try to add the column if it doesn't exist
        # But for this dev phase, the user requested a clean export/fix, so let's ensure schema is correct
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT,
            amount REAL NOT NULL,
            period TEXT CHECK(period IN ('Weekly', 'Monthly', 'Custom', 'Yearly')) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')
    except Exception as e:
        print(f"Migration warning for budgets: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
