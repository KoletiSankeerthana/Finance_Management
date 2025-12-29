import streamlit as st
from src.database.crud import reset_user_data, delete_user_account, get_user_by_email
from src.auth.security import verify_password
from src.auth.session import logout_user

def render_settings():
    # --- Defensive Hardening (V12) ---
    if not st.session_state.get('authenticated'):
        st.warning("Please log in to access settings.")
        if st.button("Go to Login"):
            st.session_state.page = "login" # Fallback if routing allows
            st.rerun()
        return

    # Ensure session state keys exist
    if 'email' not in st.session_state:
        st.session_state.email = "User"
    if 'user_id' not in st.session_state:
        st.error("Session error: User ID missing. Please re-login.")
        return
    # V13 Hero Section
    st.markdown(f"""
    <div style="margin-bottom: 25px;">
        <h1 style="margin: 0; font-size: 2.5rem; background: linear-gradient(90deg, #00b4d8, #0077b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Account Settings</h1>
        <p style="color: #a4b0be; font-size: 1.1rem; margin-top: 8px;">Optimize your financial configuration and security standards.</p>
    </div>
    """, unsafe_allow_html=True)
    
    user_id = st.session_state.user_id
    email = st.session_state.email
    
    # 1. Profile & Region Row
    col_profile, col_region = st.columns(2)
    
    with col_profile:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0 0 20px 0; color: #00b4d8; font-size: 1.2rem;">👤 Personal Identity</h3>
            <p style="font-size: 0.9rem; color: #a4b0be; margin-bottom: 5px;">Authenticated Gmail ID</p>
            <p style="font-size: 1.25rem; font-weight: 600; color: #fafafa; margin: 0;">{gmail}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_region:
        # V13: Removed redundant st.container and markdown split that caused the "extra bar"
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="margin: 0 0 10px 0; color: #00b4d8; font-size: 1.2rem;">🌍 Regional Standards</h3>', unsafe_allow_html=True)
            currency = st.selectbox("Preferred Currency", ["₹ - Indian Rupee", "$ - US Dollar", "€ - Euro"], key="set_curr")
            date_fmt = st.selectbox("Date Format", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"], key="set_date")
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 10px 15px; background: rgba(0, 180, 216, 0.05); border-left: 4px solid #00b4d8; border-radius: 4px; margin: 10px 0 25px 0;">
        <p style="margin: 0; font-size: 0.9rem; color: #00b4d8;">Note: Preferences are synchronized across all device instances and reports.</p>
    </div>
    """, unsafe_allow_html=True)

    # 3. Security & Data Management
    st.markdown("---")
    st.markdown("### 🔒 Data Operations")
    
    with st.expander("🗑️ Destructive Actions"):
        st.warning("These actions are permanent. Proceed with caution.")
        
        # Reset Data
        if st.button("Reset All Expense Data", use_container_width=True):
            st.session_state.confirm_reset = True
            
        if st.session_state.get('confirm_reset'):
            st.error("Are you sure? This will delete all transactions and categories.")
            password = st.text_input("Confirm with Password", type="password", key="reset_pass")
            col1, col2 = st.columns(2)
            if col1.button("Confirm Reset"):
                user = get_user_by_gmail(gmail)
                if verify_password(password, user['password_hash']):
                    if reset_user_data(user_id):
                        st.success("All data has been reset.")
                        st.session_state.confirm_reset = False
                        st.rerun()
                else:
                    st.error("Invalid password")
            if col2.button("Cancel"):
                st.session_state.confirm_reset = False
                st.rerun()

        st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)

        # Delete Account
        if st.button("Delete My Account Permanently", use_container_width=True, type="primary"):
            st.session_state.confirm_delete = True

        if st.session_state.get('confirm_delete'):
            st.error("CRITICAL: This will permanently delete your account and all associated data.")
            password_del = st.text_input("Confirm with Password", type="password", key="delete_pass")
            col1, col2 = st.columns(2)
            if col1.button("Permanently Delete Account"):
                user = get_user_by_gmail(gmail)
                if verify_password(password_del, user['password_hash']):
                    if delete_user_account(user_id):
                        logout_user()
                        st.rerun()
                else:
                    st.error("Invalid password")
            if col2.button("Keep My Account"):
                st.session_state.confirm_delete = False
                st.rerun()
