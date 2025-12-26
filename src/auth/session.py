import streamlit as st

def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "gmail" not in st.session_state:
        st.session_state.gmail = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

def login_user(user_id, gmail):
    st.session_state.authenticated = True
    st.session_state.user_id = user_id
    st.session_state.gmail = gmail
    st.rerun()

def logout_user():
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.gmail = None
    st.rerun()
