import streamlit as st
import os
from src.auth.session import init_session_state, logout_user
from src.auth.security import hash_password, verify_password
from src.database.crud import get_user_by_username, create_user
from src.database.schema import init_db

# Page Config
st.set_page_config(
    page_title="FinancePro | Enterprise Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Look
def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    :root {
        --primary: #00d1b2;
        --bg-dark: #0e1117;
        --card-bg: rgba(22, 27, 34, 0.7);
        --border: rgba(48, 54, 61, 0.5);
        --text-main: #fafafa;
        --text-muted: #8b949e;
    }

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: var(--text-main);
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 0%, #161b22 0%, #0e1117 100%);
    }

    /* Glassmorphism Card */
    .metric-card {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, border 0.3s ease;
        margin-bottom: 20px;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: var(--primary);
    }

    .stButton>button {
        background: linear-gradient(135deg, #00d1b2 0%, #00a896 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        box-shadow: 0 4px 15px rgba(0, 209, 178, 0.2);
    }

    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 209, 178, 0.4);
        color: white;
    }

    .sidebar-title {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(to right, #00d1b2, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        text-align: center;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    ::-webkit-scrollbar-thumb {
        background: #30363d;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #484f58;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: transparent;
        border-radius: 4px;
        color: var(--text-muted);
    }
    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom-color: var(--primary) !important;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

local_css()

# Initialize DB on first run
if not os.path.exists("finance_pro.db"):
    init_db()

# Initialize Session State
init_session_state()

# --- Authentication Pages ---
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>FinancePro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8b949e;'>Secure Enterprise Expense Management</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    user = get_user_by_username(username)
                    if user and verify_password(password, user['password_hash']):
                        st.session_state.authenticated = True
                        st.session_state.user_id = user['id']
                        st.session_state.username = user['username']
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("Username")
                new_full_name = st.text_input("Full Name")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit:
                    if not new_username or not new_password:
                        st.error("All fields are required")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif get_user_by_username(new_username):
                        st.error("Username already exists")
                    else:
                        pwd_hash = hash_password(new_password)
                        user_id = create_user(new_username, pwd_hash, new_full_name)
                        if user_id:
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error("Failed to create account")

# --- Main App Logic ---
if not st.session_state.authenticated:
    login_page()
else:
    # Authenticated Menu
    st.sidebar.markdown(f"<p class='sidebar-title'>FinancePro</p>", unsafe_allow_html=True)
    st.sidebar.markdown(f"**Welcome, {st.session_state.username}**")
    
    pages = {
        "📊 Dashboard": "dashboard",
        "🧾 Transactions": "transactions",
        "🗂️ Categories": "categories",
        "💳 Accounts": "accounts",
        "💰 Budgets": "budgets",
        "📈 Analytics": "analytics",
        "🧠 Insights": "insights",
        "📥 Import/Export": "import_export",
        "⚙️ Settings": "settings"
    }
    
    selection = st.sidebar.radio("Navigation", list(pages.keys()))
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        logout_user()

    # Dynamic Page Loading
    page_module_name = pages[selection]
    
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
        elif page_module_name == "import_export":
            from src.pages.import_export import render_import_export
            render_import_export()
        elif page_module_name == "settings":
            from src.pages.settings import render_settings
            render_settings()
            
    except Exception as e:
        st.error(f"Error loading page '{selection}': {e}")
        st.exception(e)
