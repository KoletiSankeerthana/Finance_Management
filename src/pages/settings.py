import streamlit as st
import time
from src.auth.security import change_password
from src.database.crud import reset_user_data, delete_user_account
from src.auth.session import logout_user

def render_settings():
    if not st.session_state.get('authenticated'):
        st.warning("Please log in.")
        return

    user_id = st.session_state.user_id
    username = st.session_state.get('username', "User")
    
    st.markdown(f"""
    <div style="margin-bottom: 20px; text-align: center;">
        <h1 class='app-header-title'>SETTINGS</h1>
        <p class='app-header-subtitle'>Preferences & Security</p>
    </div>
    """, unsafe_allow_html=True)

    # --- 1. Account Info ---
    st.markdown("### 👤 Account")
    st.text_input("Username", value=username, disabled=True)
    
    # --- 2. Preferences ---
    st.markdown("### ⚙️ Preferences")
    st.selectbox("Currency", ["INR (₹)", "USD ($)", "EUR (€)"], disabled=True, help="Currently fixed to INR.")
    
    st.markdown("---")

    # --- 3. Security ---
    st.markdown("### 🔒 Security")
    with st.expander("Change Password", expanded=False):
        with st.form("change_pass_form"):
            curr_pass = st.text_input("Current Password", type="password")
            new_pass = st.text_input("New Password", type="password")
            conf_pass = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Password"):
                if new_pass != conf_pass:
                    st.error("New passwords do not match.")
                elif not curr_pass or not new_pass:
                    st.error("All fields required.")
                else:
                    if change_password(username, curr_pass, new_pass):
                        st.success("Password updated successfully.")
                    else:
                        st.error("Incorrect current password.")

    st.markdown("---")

    # --- 4. Danger Zone ---
    st.markdown("### 🚨 Danger Zone")
    
    c1, c2 = st.columns(2)
    
    with c1:
        with st.expander("Reset Data"):
            st.warning("Deletes ALL transactions/budgets/categories.")
            if st.button("Reset All Data", type="primary"):
                if reset_user_data(user_id):
                    st.success("Data reset complete.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Reset failed.")
                    
    with c2:
        with st.expander("Delete Account"):
            st.warning("Permanently delete your account.")
            if st.button("Delete Account", type="primary"):
                if delete_user_account(user_id):
                    logout_user()
                    st.success("Account deleted.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Delete failed.")

    st.markdown("---")
    
    if st.button("🔓 Log Out", key="logout_btn", use_container_width=True):
        logout_user()
        st.rerun()

    from src.utils.navigation import render_bottom_nav
    render_bottom_nav("settings")
