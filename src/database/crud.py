from .schema import get_connection
import pandas as pd
import streamlit as st

# --- User Management (V33: Username + Email) ---
def create_user(username, email, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
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

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
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
        ('Transportation', ''),
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

def load_transactions_df(user_id, filters=None):
    """
    Loads transactions from SQL. 
    Strictly reads fresh data to ensure deployment sync.
    """
    conn = get_connection()
    try:
        query = "SELECT * FROM transactions WHERE user_id = ?"
        params = [user_id]
        
        if filters:
            if 'start_date' in filters and filters['start_date']:
                query += " AND date >= ?"
                params.append(filters['start_date'])
            if 'end_date' in filters and filters['end_date']:
                query += " AND date <= ?"
                params.append(filters['end_date'])
            if 'category' in filters and filters['category'] and filters['category'] != "All":
                query += " AND category = ?"
                params.append(filters['category'])
            if 'payment_mode' in filters and filters['payment_mode'] and filters['payment_mode'] != "All":
                query += " AND payment_method = ?"
                params.append(filters['payment_mode'])
        
        query += " ORDER BY date DESC"
        df = pd.read_sql(query, conn, params=params)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            
        return df
    finally:
        conn.close()

    return df

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
        return True
    except Exception as e:
        print(f"Error adding transaction: {e}")
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

def add_budget(user_id, category, amount, period, start_date, end_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if exists
        cursor.execute(
            "SELECT id FROM budgets WHERE user_id = ? AND category = ? AND period = ?",
            (user_id, category, period)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update
            cursor.execute(
                "UPDATE budgets SET amount = ?, start_date = ?, end_date = ? WHERE id = ?",
                (amount, start_date, end_date, existing[0])
            )
        else:
            # Insert
            cursor.execute(
                "INSERT INTO budgets (user_id, category, amount, period, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, category, amount, period, start_date, end_date)
            )
        conn.commit()
        return True
    except Exception as e: 
        print(f"Error adding budget: {e}")
        return False
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
def get_most_used_category(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, COUNT(category) as count 
        FROM transactions 
        WHERE user_id = ? 
        GROUP BY category 
        ORDER BY count DESC 
        LIMIT 1
    """, (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res['category'] if res else None

def update_transaction(transaction_id, user_id, amount, category, payment_method, date, notes):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE transactions 
            SET amount = ?, category = ?, payment_method = ?, date = ?, notes = ?
            WHERE id = ? AND user_id = ?
        """, (amount, category, payment_method, date, notes, transaction_id, user_id))
        conn.commit()
        _clear_cache()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating transaction: {e}")
        return False
    finally: conn.close()
