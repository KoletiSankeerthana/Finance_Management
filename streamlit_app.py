# Force reload
import streamlit as st
# V35: Force Reload - CRUD Fixed
import sqlite3
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from src.auth.session import init_session_state, login_user, logout_user
from src.auth.security import hash_password, verify_password
from src.database.crud import (
    create_user, get_user_by_email, update_password_by_email
)
from src.database.schema import init_db
from src.utils.constants import APP_TITLE, APP_SUBTITLE, PRIMARY_COLOR
import random
import time
st.set_page_config(
    page_title="Expense Tracker | Smart & Simple",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
def local_css():
    st.markdown("""
    <style>
    /* Strict Font Enforcement: Times New Roman */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Outfit:wght@300;400;600;700&family=Inter:wght@400;500;600&display=swap');
    
    :root {
        --primary: #008080; /* Professional Teal */
        --secondary: #005f5f;
        --bg-main: #0b0e14;
        --bg-card: #161b22;
        --text-main: #fafafa;
        --text-muted: #a4b0be;
        --border: rgba(255, 255, 255, 0.08);
        /* Force Times New Roman globally as per strict rules */
        --font-elegant: 'Times New Roman', serif;
        --font-modern: 'Times New Roman', serif;
        --font-body: 'Times New Roman', serif; 
    }

    /* Global Typography Reset */
    .main .block-container, .stApp, h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stButton button, .caption, .small-text {
        font-family: 'Times New Roman', serif !important;
        color: var(--text-main);
    }
    
    .stApp {
        background-color: var(--bg-main);
    }
    
    .app-header-title {
        font-weight: 700 !important;
        font-size: 3.5rem !important;
        text-transform: uppercase !important;
        text-align: center !important;
        background: linear-gradient(180deg, #ffffff 0%, #a4b0be 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .app-header-subtitle {
        font-weight: 300 !important;
        font-size: 1.2rem !important;
        text-align: center !important;
        opacity: 0.7;
        letter-spacing: 2px;
        margin-top: -10px !important;
    }
    
    /* Input & Elements */
    input, textarea, select, .stTextInput input, .stSelectbox [data-baseweb="select"] {
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        background-color: #1c2128 !important;
        padding: 12px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2) !important;
        font-family: 'Times New Roman', serif !important;
    }
    
    /* Sidebar */
    .stSidebar {
        background-color: #0d1117 !important; # Darker sidebar
        border-right: 1px solid var(--border);
    }
    
    #MainMenu, header, footer {visibility: hidden;}
    
    /* Buttons */
    .stButton>button {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background: var(--secondary) !important;
        transform: scale(1.02) !important;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Initialize DB and ensure schema consistency
init_db()

# Initialize Session State
init_session_state()

# --- Authentication Pages ---
def login_page():
    # Persistent Notifications
    if st.session_state.get('auth_notification'):
        ntype, nmsg = st.session_state.auth_notification
        if ntype == "success": st.success(nmsg)
        else: st.error(nmsg)
        del st.session_state.auth_notification

    # Centered container for professional look
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style='text-align: center; padding: 40px 0;'>
            <h1 class='app-header-title'>{APP_TITLE}</h1>
            <p class='app-header-subtitle'>{APP_SUBTITLE}</p>
            <div style='width: 60px; height: 3px; background: var(--primary); margin: 20px auto; border-radius: 2px;'></div>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Login", "Register", "Forgot Password"])
        
        with tab1:
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email Address")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    user = get_user_by_email(email)
                    if user and verify_password(password, user['password_hash']):
                        login_user(user['id'], user['email'])
                    else:
                        st.error("Invalid Email or password.")
        
        with tab2:
            with st.form("register_form"):
                new_email = st.text_input("Email Address")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit:
                    if not new_email or not new_password:
                        st.error("All fields are required")
                    elif "@" not in new_email or "." not in new_email:
                        st.error("Please provide a valid email address")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 8:
                        st.error("Password must be at least 8 characters.")
                    elif get_user_by_email(new_email):
                        st.error("Account already exists. Please log in.")
                    else:
                        pwd_hash = hash_password(new_password)
                        user_id = create_user(new_email, pwd_hash)
                        if user_id:
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error("Failed to create account")
                            
        with tab3:
            st.markdown("### 🔑 Reset Password (Demo Mode)")
            
            if not st.session_state.get("reset_email"):
                st.info("Enter your registered email to generate a demo OTP.")
                with st.form("otp_generate_form"):
                    email_input = st.text_input("Registered Email Address")
                    generate_btn = st.form_submit_button("Generate OTP", use_container_width=True)
                    
                    if generate_btn:
                        user = get_user_by_email(email_input)
                        if user:
                            otp = str(random.randint(100000, 999999))
                            st.session_state.reset_otp = otp
                            st.session_state.reset_email = email_input
                            st.session_state.otp_expiry = datetime.now() + timedelta(minutes=5)
                            st.session_state.otp_verified = False
                            st.rerun()
                        else:
                            st.error("No account found with this email.")
            
            elif st.session_state.get("reset_email") and not st.session_state.get("otp_verified"):
                st.warning(f"🔧 **DEV MODE OTP: {st.session_state.reset_otp}**")
                
                with st.form("otp_verify_form"):
                    input_otp = st.text_input("Enter 6-digit OTP", placeholder="123456")
                    verify_btn = st.form_submit_button("Verify OTP", use_container_width=True)
                    
                    if verify_btn:
                        if datetime.now() > st.session_state.otp_expiry:
                            st.error("OTP expired.")
                            st.session_state.reset_email = None
                        elif input_otp == st.session_state.reset_otp:
                            st.session_state.otp_verified = True
                            st.success("OTP Verified!")
                            st.rerun()
                        else:
                            st.error("Invalid OTP.")
                
                if st.button("Cancel & Restart"):
                    st.session_state.reset_email = None
                    st.rerun()

            elif st.session_state.get("otp_verified"):
                st.success(f"Verified for: {st.session_state.reset_email}")
                with st.form("new_password_form_otp"):
                    new_pass = st.text_input("New Password", type="password", placeholder="Min 8 chars")
                    conf_pass = st.text_input("Confirm Password", type="password")
                    reset_btn = st.form_submit_button("Reset Password", use_container_width=True)
                    
                    if reset_btn:
                        if new_pass != conf_pass:
                            st.error("Passwords do not match.")
                        elif len(new_pass) < 8:
                            st.error("Min 8 characters required.")
                        else:
                            if update_password_by_email(st.session_state.reset_email, hash_password(new_pass)):
                                st.success("Password reset successful!")
                                st.session_state.reset_email = None
                                st.session_state.reset_otp = None
                                st.session_state.otp_verified = False
                                st.info("Please sign in.")
                            else:
                                st.error("Failed to update password.")
                
                if st.button("Cancel"):
                    st.session_state.reset_email = None
                    st.rerun()

# --- Main App Logic ---
# ROUTING SYSTEM (V42: Persistent Sidebar + Toggle)
NAV_CONFIG = {
    "Home": {"icon": "🏠", "render": "render_intro", "import": "src.pages.intro"},
    "Dashboard": {"icon": "📊", "render": "render_dashboard", "import": "src.pages.dashboard"},
    "Expenses": {"icon": "📄", "render": "render_transactions", "import": "src.pages.transactions"},
    "Categories": {"icon": "🗂️", "render": "render_categories", "import": "src.pages.categories"},
    "Analytics": {"icon": "📈", "render": "render_analytics", "import": "src.pages.analytics"},
    "Budgets": {"icon": "💰", "render": "render_budgets", "import": "src.pages.budgets"},
    "Settings": {"icon": "⚙️", "render": "render_settings", "import": "src.pages.settings"}
}

if not st.session_state.authenticated:
    login_page()
else:
    # Sidebar Toggle & Styling
    expanded = st.session_state.sidebar_expanded
    
    # CSS for Sidebar Width control
    sidebar_width = "280px" if expanded else "80px"
    st.markdown(f"""
        <style>
        [data-testid="stSidebar"] {{
            min-width: {sidebar_width} !important;
            max-width: {sidebar_width} !important;
            transition: all 0.3s ease-in-out;
        }}
        [data-testid="stSidebarNav"] {{ display: none; }} /* Hide default nav */
        
        .nav-btn {{
            display: flex;
            align-items: center;
            padding: 10px;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 5px;
            transition: background 0.2s;
        }}
        .nav-btn:hover {{ background: rgba(255,255,255,0.05); }}
        .nav-active {{ background: rgba(0, 128, 128, 0.2) !important; border-left: 3px solid #008080; }}
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Toggle Button (<< >>)
        toggle_label = "<<" if expanded else ">>"
        if st.button(toggle_label, key="sidebar_toggle", help="Expand/Collapse Sidebar"):
            st.session_state.sidebar_expanded = not st.session_state.sidebar_expanded
            st.rerun()

        if expanded:
            st.markdown(f"""
            <div style='padding: 0 0 20px 0;'>
                <p style='font-size:1.5rem; font-weight:bold; color:var(--primary); margin:0;'>{APP_TITLE}</p>
                <p style='font-size: 0.75rem; color:var(--text-muted);'>{APP_SUBTITLE}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"👤 **{st.session_state.email}**")
            st.markdown("---")
        else:
            st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

        # Navigation Menu
        for label, config in NAV_CONFIG.items():
            is_active = st.session_state.current_page == label
            
            # Use buttons for navigation to ensure persistence and instant updates
            btn_label = f"{config['icon']} {label}" if expanded else config['icon']
            
            if st.button(
                btn_label, 
                key=f"nav_{label}", 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = label
                st.rerun()

        st.markdown("---")
        if st.button("🔓 Logout", use_container_width=True, key="sidebar_logout"):
            logout_user()

    # Route Rendering
    curr_page_label = st.session_state.current_page
    if curr_page_label not in NAV_CONFIG:
        curr_page_label = "Dashboard"
        st.session_state.current_page = "Dashboard"

    config = NAV_CONFIG[curr_page_label]
    
    # Dynamic Import and Call
    import importlib
    module = importlib.import_module(config['import'])
    content_func = getattr(module, config['render'])
    content_func()
