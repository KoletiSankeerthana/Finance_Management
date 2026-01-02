# V36: Mobile UI Fix - Force Deployment Trigger
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
        font-size: clamp(1.8rem, 8vw, 3rem) !important; /* Optimized scaling */
        white-space: nowrap !important;
        text-transform: uppercase !important;
        text-align: center !important;
        background: linear-gradient(180deg, #ffffff 0%, #a4b0be 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: block;
        width: 100%;
        margin: 0 auto !important;
        overflow: hidden;
        text-overflow: ellipsis;
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
        background-color: #0d1117 !important;
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

    /* Floating Toggle Styling */
    .custom-hamburger {
        position: fixed;
        top: 15px;
        left: 15px;
        z-index: 999999;
        background: var(--bg-card);
        color: white;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
        border: 1px solid var(--border);
        transition: all 0.2s ease;
    }
    .custom-hamburger:hover {
        background: var(--primary);
        transform: scale(1.1);
    }
    /* Hide the trigger button itself */
    div.stButton > button[key^="mobile_toggle"] {
        display: none !important;
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
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    from src.auth.security import get_user_by_username
                    user = get_user_by_username(username)
                    if user:
                        # Convert SQLite Row to dict for easier access
                        user_dict = dict(user) if hasattr(user, 'keys') else {
                            'id': user[0],
                            'username': user[1],
                            'password_hash': user[3]
                        }
                        
                        if verify_password(password, user_dict['password_hash']):
                            login_user(user_dict['id'], user_dict['username'])
                        else:
                            st.error("Invalid username or password.")
                    else:
                        st.error("Invalid username or password.")
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("Username", help="Choose a unique username")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit:
                    if not new_username or not new_password:
                        st.error("All fields are required")
                    elif len(new_username) < 3:
                        st.error("Username must be at least 3 characters")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 8:
                        st.error("Password must be at least 8 characters.")
                    else:
                        from src.auth.security import get_user_by_username
                        if get_user_by_username(new_username):
                            st.error("Username already taken. Please choose another.")
                        else:
                            pwd_hash = hash_password(new_password)
                            user_id = create_user(new_username, pwd_hash)
                            if user_id:
                                st.success("Account created successfully! Please login.")
                            else:
                                st.error("Failed to create account")
                            
        # Forgot Password Tab Removed as per user request
                
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
from src.utils.navigation import render_sidebar, NAV_CONFIG

if not st.session_state.authenticated:
    login_page()
else:
    # Render centralized responsive sidebar
    render_sidebar()

    # Route Rendering
    curr_page_label = st.session_state.get('current_page', 'Dashboard')
    if curr_page_label not in NAV_CONFIG:
        curr_page_label = "Dashboard"
        st.session_state.current_page = "Dashboard"

    config = NAV_CONFIG[curr_page_label]
    
    # Dynamic Import and Call
    import importlib
    module = importlib.import_module(config['import'])
    content_func = getattr(module, config['render'])
    content_func()
