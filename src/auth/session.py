import streamlit as st

def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"  # Changed to Home as landing page
    if "sidebar_expanded" not in st.session_state:
        st.session_state.sidebar_expanded = True
    
    # Old key migration (optional safety)
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
    
    # Password Reset States (Modified for Username)
    if "reset_otp" not in st.session_state:
        st.session_state.reset_otp = None
    if "reset_username" not in st.session_state:
        st.session_state.reset_username = None
    if "otp_expiry" not in st.session_state:
        st.session_state.otp_expiry = None
    if "otp_verified" not in st.session_state:
        st.session_state.otp_verified = False

def login_user(user_id, username):
    st.session_state.authenticated = True
    st.session_state.user_id = user_id
    st.session_state.username = username
    st.rerun()

def logout_user():
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()
