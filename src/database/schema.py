import sqlite3
import os

DB_PATH = "finance_pro.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode and stability pragmas for cloud deployment
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    return conn

def migrate_users_to_nullable_email(cursor):
    """
    Migration: SQLite doesn't support ALTER TABLE ... MODIFY COLUMN.
    We need to rename, create new, and copy.
    """
    try:
        # Check if email is NOT NULL
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        email_col = next((col for col in columns if col['name'] == 'email'), None)
        
        # if email_col['notnull'] == 1, then it's NOT NULL and we need to migrate
        if email_col and email_col['notnull'] == 1:
            print("Migrating users table to make email nullable...")
            
            # Check if users_old already exists (from a failed previous run)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users_old'")
            if cursor.fetchone():
                cursor.execute("DROP TABLE users_old")

            # 1. Rename old table
            cursor.execute("ALTER TABLE users RENAME TO users_old")
            
            # 2. Create new table with nullable email
            cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 3. Copy data
            # To avoid UNIQUE constraint failures on username, we'll append the id if the prefix is not unique
            # But for simplicity and safety of duplicates, let's just use the ID as a suffix for all MIGRATED users 
            # OR use a more clever approach. Let's try prefix_id for conflict cases.
            cursor.execute('''
            INSERT INTO users (id, username, email, password_hash, created_at)
            SELECT id, 
                   COALESCE(username, SUBSTR(email, 1, INSTR(email, '@') - 1)) || '_' || id,
                   email, 
                   password_hash, 
                   created_at
            FROM users_old
            ''')
            
            # 4. Drop old table
            cursor.execute("DROP TABLE users_old")
            print("Migration successful.")
    except Exception as e:
        print(f"Migration error (nullable email): {e}")

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users Table Shell (Ensure table exists first)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. Migration: Add username column if missing from very old versions
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = [col['name'] for col in cursor.fetchall()]
        if 'username' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
            cursor.execute("""
                UPDATE users 
                SET username = SUBSTR(email, 1, INSTR(email, '@') - 1)
                WHERE username IS NULL
            """)
    except Exception as e:
        print(f"Migration error (username column): {e}")

    # 3. Migration: Make email nullable
    migrate_users_to_nullable_email(cursor)
    
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
