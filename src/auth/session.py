import streamlit as st

def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "email" not in st.session_state:
        st.session_state.email = None
    if "page" not in st.session_state:
        st.session_state.page = "welcome"
    
    # OTP States (Demo Only)
    if "reset_otp" not in st.session_state:
        st.session_state.reset_otp = None
    if "reset_email" not in st.session_state:
        st.session_state.reset_email = None
    if "otp_expiry" not in st.session_state:
        st.session_state.otp_expiry = None
    if "otp_verified" not in st.session_state:
        st.session_state.otp_verified = False

def login_user(user_id, email):
    st.session_state.authenticated = True
    st.session_state.user_id = user_id
    st.session_state.email = email
    st.rerun()

def logout_user():
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.email = None
    st.rerun()
