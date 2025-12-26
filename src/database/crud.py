from .schema import get_connection
import pandas as pd
import streamlit as st

# --- User Management (V11: Gmail Enforced) ---
def create_user(gmail, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (gmail, password_hash) VALUES (?, ?)",
            (gmail, password_hash)
        )
        user_id = cursor.lastrowid
        init_user_defaults(user_id, cursor)
        conn.commit()
        return user_id
    except Exception as e:
        print(f"Error creating user: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_user_by_gmail(gmail):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE gmail = ?", (gmail,))
    user = cursor.fetchone()
    conn.close()
    return user

def set_reset_token(user_id, token):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET reset_token = ? WHERE id = ?", (token, user_id))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def update_password(user_id, new_password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET password_hash = ?, reset_token = NULL WHERE id = ?", 
                       (new_password_hash, user_id))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def init_user_defaults(user_id, cursor=None):
    conn = None
    if cursor is None:
        conn = get_connection()
        cursor = conn.cursor()
    
    # V3: Default categories with Emojis
    default_categories = [
        ('Food & Dining', '🍔'),
        ('Transportation', '🚕'),
        ('Shopping', '🛒'),
        ('Utilities', '💡'),
        ('Entertainment', '🎬'),
        ('Health', '🏥'),
        ('Education', '📚'),
        ('Others', '🏷️')
    ]
    cursor.executemany(
        "INSERT INTO categories (user_id, name, emoji) VALUES (?, ?, ?)",
        [(user_id, *cat) for cat in default_categories]
    )
    
    if conn:
        conn.commit()
        conn.close()

# --- Category Management ---
def get_categories(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE user_id = ?", (user_id,))
    categories = cursor.fetchall()
    conn.close()
    return categories

def add_category(user_id, name, emoji):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (user_id, name, emoji) VALUES (?, ?, ?)",
                       (user_id, name, emoji))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def delete_category(user_id, category_name):
    conn = get_connection()
    cursor = conn.cursor()
    # Deletion Safety (V3 requirement)
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ? AND category = ?", (user_id, category_name))
    count = cursor.fetchone()[0]
    if count > 0:
        conn.close()
        return False, f"Cannot delete '{category_name}': It is linked to {count} transactions."
    
    cursor.execute("DELETE FROM categories WHERE user_id = ? AND name = ?", (user_id, category_name))
    conn.commit()
    conn.close()
    return True, "Category deleted successfully."

def get_category_map(user_id):
    """Returns a Dict mapping category name to its Emoji"""
    cats = get_categories(user_id)
    return {c['name']: c['emoji'] for c in cats}

# --- Caching & Validation (V6 Architecture) ---
@st.cache_data(ttl=60, show_spinner=False)
def load_transactions_df(user_id, filters=None):
    """
    V6 Architecture: Single Source of Truth with Caching
    - Caches DB reads for performance
    - Enforces strict schema validation
    - Handles empty states gracefully
    """
    conn = get_connection()
    query = "SELECT * FROM transactions WHERE user_id = ?"
    params = [user_id]
    
    if filters:
        if 'start_date' in filters and filters['start_date']:
            query += " AND date >= ?"
            params.append(filters['start_date'])
        if 'end_date' in filters and filters['end_date']:
            query += " AND date <= ?"
            params.append(filters['end_date'])
        if 'search' in filters and filters['search']:
            # Multidimensional search logic
            s = f"%{filters['search']}%"
            query += " AND (category LIKE ? OR notes LIKE ? OR date LIKE ?)"
            params.extend([s, s, s])
            
    try:
        df = pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        print(f"DB Read Error: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    
    # Global Schema Validation
    required_columns = ['id', 'user_id', 'amount', 'category', 'payment_method', 'date', 'notes', 'created_at']
    if df.empty:
        return pd.DataFrame(columns=required_columns)
    
    # Defensive Date Parsing
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']) # Drop corrupted rows
    
    # Ensure all columns exist (defensive schema)
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
            
    return df

def _clear_cache():
    load_transactions_df.clear()

# --- Transaction Management ---
def add_transaction(user_id, amount, category, payment_method, date, notes):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # V3 Ensure amount is stored as positive
        abs_amount = abs(float(amount))
        cursor.execute(
            """INSERT INTO transactions (user_id, amount, category, payment_method, date, notes) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, abs_amount, category, payment_method, date, notes)
        )
        conn.commit()
        _clear_cache() # V6: Invalidate cache on write
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def delete_transaction(transaction_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id))
        conn.commit()
        _clear_cache() # V6: Invalidate cache on delete
        return True
    except: return False
    finally: conn.close()

# --- Budget Management ---
def get_budgets(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budgets WHERE user_id = ?", (user_id,))
    budgets = cursor.fetchall()
    conn.close()
    return budgets

def add_budget(user_id, category, amount, period, start_date):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO budgets (user_id, category, amount, period, start_date) VALUES (?, ?, ?, ?, ?)",
            (user_id, category, amount, period, start_date)
        )
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def delete_budget(budget_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM budgets WHERE id = ? AND user_id = ?", (budget_id, user_id))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- Reset Management ---
def reset_user_data(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM budgets WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM categories WHERE user_id = ?", (user_id,))
        init_user_defaults(user_id, cursor)
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def delete_user_account(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True
    except: return False
    finally: conn.close()
