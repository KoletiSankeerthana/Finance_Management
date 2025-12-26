import streamlit as st
import os
import re
import secrets
from src.auth.session import init_session_state, logout_user
from src.auth.security import hash_password, verify_password
from src.database.crud import (
    create_user, get_user_by_gmail, 
    set_reset_token, update_password
)
from src.database.schema import init_db

# Page Config
st.set_page_config(
    page_title="FinancePro | Executive Insight Dashboard",
    page_icon="💸",
    layout="wide",
)

# Global Bottom Navigation Logic
def render_bottom_nav(current_page):
    st.markdown("---")
    pages = ["dashboard", "transactions", "categories", "budgets", "analytics", "insights", "settings"]
    labels = ["Dashboard", "Transactions", "Categories", "Budgets", "Analytics", "Insights", "Settings"]
    
    try:
        idx = pages.index(current_page)
    except ValueError:
        return

    col_prev, col_spacer, col_next = st.columns([1, 2, 1])
    
    # Previous Button
    if idx > 0:
        prev_page = pages[idx - 1]
        prev_label = labels[idx - 1]
        if col_prev.button(f"⬅️ {prev_label}", key="nav_prev", use_container_width=True):
            st.session_state.page = prev_page
            st.rerun()
            
    # Next Button
    if idx < len(pages) - 1:
        next_page = pages[idx + 1]
        next_label = labels[idx + 1]
        if col_next.button(f"{next_label} ➡️", key="nav_next", use_container_width=True):
            st.session_state.page = next_page
            st.rerun()

# Custom CSS for Premium Look
def local_css():
    st.markdown("""
    <style>
    /* V13 Professional Typography & Branding */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@400;500;600&display=swap');
    
    :root {
        --primary: #00b4d8;
        --secondary: #0077b6;
        --bg-main: #0b0e14;
        --bg-card: #161b22;
        --text-main: #fafafa;
        --text-muted: #a4b0be;
        --border: rgba(255, 255, 255, 0.08);
        --font-modern: 'Outfit', sans-serif;
        --font-body: 'Inter', sans-serif;
        --font-serif: 'Times New Roman', Times, serif;
    }

    /* Global Typography Reset */
    .main .block-container, .stApp {
        font-family: var(--font-body) !important;
        background-color: var(--bg-main);
        color: var(--text-main);
    }
    
    h1, h2, h3, .sidebar-title {
        font-family: var(--font-modern) !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* V13: Force Times New Roman on smaller text per user request */
    /* V14: Scaled down to 0.88rem for better visibility in bars */
    p, span, small, label, .stMarkdown p, .stMarkdown li {
        font-family: var(--font-serif) !important;
        font-size: 0.88rem !important;
        line-height: 1.4;
    }
    
    /* Specific override for input text content */
    .stTextInput input, .stSelectbox [data-testid="stMarkdownContainer"] p, .stNumberInput input {
        font-size: 0.88rem !important;
    }
    
    /* Executive Card Styling */
    .metric-card {
        background: var(--bg-card);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid var(--border);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 20px;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 180, 216, 0.3);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }

    /* Sidebar Refinement */
    .stSidebar {
        background-color: #0d1117 !important;
    }
    .sidebar-title {
        font-size: 1.8rem;
        color: var(--primary);
        margin-bottom: 1.5rem;
        text-align: center;
    }

    /* V13 Sidebar Navigation Navigation */
    div[role="radiogroup"] > label {
        background-color: transparent !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        margin-bottom: 6px !important;
        transition: all 0.2s ease !important;
        border: 1px solid transparent !important;
    }
    div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: rgba(0, 180, 216, 0.1) !important;
        border: 1px solid rgba(0, 180, 216, 0.3) !important;
        color: var(--primary) !important;
    }
    
    /* Professional Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00b4d8 0%, #0077b6 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 10px !important;
        font-family: var(--font-modern) !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 180, 216, 0.3) !important;
    }

    /* Hidden Streamlit Elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

local_css()

# Initialize DB and ensure schema consistency
init_db()

# Initialize Session State
init_session_state()

# --- Authentication Pages ---
def login_page():
    # Centered container for professional look
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h1 style='margin: 0; font-size: 2.5rem; background: linear-gradient(90deg, #00b4d8, #0077b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>FinancePro</h1>
            <p style='color: #8b949e; font-size: 1.1rem;'>Professional Expense Management</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Login", "Register", "Forgot Password"])
        
        with tab1:
            with st.form("login_form", clear_on_submit=False):
                gmail = st.text_input("Gmail ID", placeholder="yourname@gmail.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    user = get_user_by_gmail(gmail)
                    if user and verify_password(password, user['password_hash']):
                        st.session_state.authenticated = True
                        st.session_state.user_id = user['id']
                        st.session_state.gmail = user['gmail']
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("Invalid Gmail or password.")
        
        with tab2:
            with st.form("register_form"):
                new_gmail = st.text_input("Gmail ID", placeholder="yourname@gmail.com")
                new_password = st.text_input("Password", type="password", placeholder="Minimum 8 characters")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit:
                    if not new_gmail or not new_password:
                        st.error("All fields are required")
                    elif not re.match(r"[^@]+@gmail\.com", new_gmail):
                        st.error("Please provide a valid @gmail.com address")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif get_user_by_gmail(new_gmail):
                        st.error("Account already exists. Please log in.")
                    else:
                        pwd_hash = hash_password(new_password)
                        user_id = create_user(new_gmail, pwd_hash)
                        if user_id:
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error("Failed to create account")
                            
        with tab3:
            st.markdown("### Reset Password")
            gmail_reset = st.text_input("Enter your registered Gmail ID")
            if st.button("Send Reset Link", use_container_width=True):
                user = get_user_by_gmail(gmail_reset)
                if user:
                    token = secrets.token_urlsafe(16)
                    set_reset_token(user['id'], token)
                    st.info(f"SUCCESS: A reset token has been simulated for {gmail_reset}.")
                    st.session_state.reset_email = gmail_reset
                    st.session_state.reset_active = True
                else:
                    st.error("No account found with this Gmail ID.")
            
            if st.session_state.get('reset_active'):
                st.markdown("---")
                st.markdown("#### Enter New Credentials")
                new_pwd = st.text_input("New Password", type="password")
                confirm_new_pwd = st.text_input("Confirm New Password", type="password")
                if st.button("Set New Password"):
                    if new_pwd == confirm_new_pwd and len(new_pwd) >= 8:
                        user = get_user_by_gmail(st.session_state.reset_email)
                        if update_password(user['id'], hash_password(new_pwd)):
                            st.success("Password updated successfully! You can now login.")
                            st.session_state.reset_active = False
                        else:
                            st.error("Failed to update password.")
                    else:
                        st.error("Passwords must match and be at least 8 characters.")

# --- Main App Logic ---
if not st.session_state.authenticated:
    login_page()
else:
    # Authenticated Menu
    st.sidebar.markdown(f"<p class='sidebar-title'>FinancePro</p>", unsafe_allow_html=True)
    st.sidebar.markdown(f"**Welcome, {st.session_state.gmail}**")
    
    pages = {
        "📊 Dashboard": "dashboard",
        "🧾 Transactions": "transactions",
        "🗂️ Categories": "categories",
        "💰 Budgets": "budgets",
        "📈 Analytics": "analytics",
        "🧠 Insights": "insights",
        "⚙️ Settings": "settings"
    }
    
    # Reverse lookup for radio index
    page_keys = list(pages.keys())
    page_values = list(pages.values())
    
    # Ensure session state page is valid
    if "page" not in st.session_state or st.session_state.page not in page_values:
        st.session_state.page = "dashboard"
        
    current_index = page_values.index(st.session_state.page)
    
    selection = st.sidebar.radio("Navigation", page_keys, index=current_index)
    
    # Update session state if radio changed
    if pages[selection] != st.session_state.page:
        st.session_state.page = pages[selection]
        st.rerun()
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        logout_user()

    # Dynamic Page Loading
    page_module_name = st.session_state.page
    
    # Render the selected page
    try:
        # Instead of importing dynamically (which is messy in Streamlit), 
        # we will call functions from a router or similar.
        # For now, I'll use a simple if/elif but ideally we'd have modular page functions.
        
        if page_module_name == "dashboard":
            from src.pages.dashboard import render_dashboard
            render_dashboard()
        elif page_module_name == "transactions":
            from src.pages.transactions import render_transactions
            render_transactions()
        elif page_module_name == "categories":
            from src.pages.categories import render_categories
            render_categories()
        elif page_module_name == "accounts":
            from src.pages.accounts import render_accounts
            render_accounts()
        elif page_module_name == "budgets":
            from src.pages.budgets import render_budgets
            render_budgets()
        elif page_module_name == "analytics":
            from src.pages.analytics import render_analytics
            render_analytics()
        elif page_module_name == "insights":
            from src.pages.insights import render_insights
            render_insights()
        elif page_module_name == "settings":
            from src.pages.settings import render_settings
            render_settings()
            
        # V7 Global Bottom Navigation
        render_bottom_nav(page_module_name)
            
    except Exception as e:
        st.error(f"Error loading page '{selection}': {e}")
        st.exception(e)
