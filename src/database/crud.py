from .schema import get_connection
import pandas as pd
import streamlit as st

# --- User Management (V32: Email Enforced) ---
def create_user(email, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash)
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

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user


def update_password(user_id, new_password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", 
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

def get_transactions(user_id):
    # V6: Caching
    cache_key = f"tx_{user_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    conn = get_connection()
    # Return as DataFrame for easy analysis
    df = pd.read_sql("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", conn, params=(user_id,))
    conn.close()
    
    # Store in session state cache
    st.session_state[cache_key] = df
    return df

def _clear_cache():
    # Helper to clear transaction cache
    keys = [k for k in st.session_state.keys() if k.startswith("tx_")]
    for k in keys:
        del st.session_state[k]

# --- Transaction Management ---
def add_transaction(user_id, amount, category, payment, date, notes):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO transactions (user_id, amount, category, payment_method, date, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, amount, category, payment, date, notes)
        )
        conn.commit()
        _clear_cache() # V6: Invalidate cache
        return True
    except Exception as e:
        print(e)
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

# --- Password Reset Flow (V32) ---


def update_password_by_email(email, hashed_password):
    """Updates the user's password using email identifier."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET password_hash = ? WHERE email = ?', (hashed_password, email))
        conn.commit()
        return cursor.rowcount > 0
    finally: conn.close()
