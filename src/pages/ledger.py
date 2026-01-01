import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from src.database.crud import load_transactions_df, delete_transaction
from src.utils.formatting import format_currency
from src.utils.constants import CATEGORIES, CATEGORY_ICONS, PAYMENT_MODES

def render_ledger():
    if not st.session_state.get('authenticated'):
        st.warning("Please log in to access your ledger.")
        return
    
    user_id = st.session_state.user_id
    
    # Hero Section
    st.markdown(f"""
    <div style="margin-bottom: 30px; text-align: center;">
        <h1 class='app-header-title'>EXPENSES</h1>
        <p class='app-header-subtitle'>Full transaction history and record management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Load Data Base ---
    df_raw = load_transactions_df(user_id)
    
    if df_raw.empty:
        st.info("No expense records found. Record your first movement to see history!")
        return


    # --- DELETE SECTION (Moved from Transactions) ---
    with st.expander("🗑️ Delete Transaction", expanded=False):
        st.markdown("##### Find Transaction to Delete")
        
        # 1. Search Inputs
        dc1, dc2 = st.columns(2)
        target_cat = dc1.selectbox("Category (Mandatory)", ["Select"] + CATEGORIES, key="led_del_cat")
        target_mode = dc2.selectbox("Mode (Optional)", ["Any"] + PAYMENT_MODES, key="led_del_mode")
        
        dc3, dc4 = st.columns(2)
        target_amt = dc3.number_input("Amount (Optional)", min_value=0.0, step=1.0, key="led_del_amt")
        target_date_enable = dc4.checkbox("Filter by Date", key="led_del_dt_chk")
        target_date = dc4.date_input("Date", value=datetime.now(), disabled=not target_date_enable, key="led_del_dt")
        
        if st.button("🔍 Find Records", key="led_btn_find", use_container_width=True):
            if target_cat == "Select":
                st.error("⚠️ Category must be selected.")
            else:
                # Search Logic
                df_all = load_transactions_df(user_id)
                if not df_all.empty:
                    mask = (df_all['category'] == target_cat)
                    
                    if target_mode != "Any":
                        mask = mask & (df_all['payment_method'] == target_mode)
                    
                    if target_amt > 0:
                        # Allow small float diff
                        mask = mask & (abs(df_all['amount'] - target_amt) < 0.1)
                        
                    if target_date_enable:
                        mask = mask & (df_all['date'].dt.date == target_date)
                        
                    matches = df_all[mask].copy()
                    if not matches.empty:
                        st.session_state['led_del_matches'] = matches
                        st.success(f"Found {len(matches)} matches.")
                    else:
                        st.warning("No matches found.")
                        if 'led_del_matches' in st.session_state: del st.session_state['led_del_matches']
                else: st.warning("No records at all.")

        # 2. Display & Action
        if 'led_del_matches' in st.session_state and not st.session_state['led_del_matches'].empty:
            matches = st.session_state['led_del_matches']
            st.markdown("---")
            st.markdown("###### Select Record to Delete:")
            
            # Format label
            matches['label'] = matches.apply(
                lambda x: f"{x['date'].strftime('%Y-%m-%d')} | ₹{x['amount']} | {x['notes'] or ''}", axis=1
            )
            
            del_sel = st.radio("Matching Records:", matches['label'].tolist(), key="led_del_radio")
            
            if st.button("❌ Delete Selected Record", key="led_btn_act_del", type="primary"):
                 rec_id = matches[matches['label'] == del_sel].iloc[0]['id']
                 if delete_transaction(rec_id, user_id):
                     st.success("Deleted successfully!")
                     del st.session_state['led_del_matches']
                     time.sleep(1)
                     st.rerun()
                 else:
                     st.error("Failed to delete.")


    st.markdown("### 🔍 Filter Records")
    with st.container():
        # Row 1: Period, Category, Mode
        c1, c2, c3 = st.columns(3)
        # Default index=2 for "Monthly"
        period = c1.selectbox("View Period", ["Daily", "Weekly", "Monthly", "Custom"], index=2, key="led_period_final")
        sel_cat = c2.selectbox("Category", ["All"] + CATEGORIES, key="led_cat_final")
        sel_mode = c3.selectbox("Payment Mode", ["All", "Cash", "UPI", "Debit Card", "Credit Card"], key="led_mode_final")
        
        # Row 2: Custom Date (Only if selected)
        # Row 2: Custom Date (Only if selected) & Amount Range
        c_r2_1, c_r2_2, c_r2_3 = st.columns([2, 1, 1])
        
        with c_r2_1:
            if period == "Custom":
                 c_date_1, c_date_2 = st.columns(2)
                 start_d = c_date_1.date_input("From Date", value=datetime.now() - timedelta(days=7))
                 end_d = c_date_2.date_input("To Date", value=datetime.now())
            else:
                 # Date Logic
                 now = datetime.now().date()
                 start_d, end_d = None, None
                 
                 if period == "Daily":
                     start_d, end_d = now, now
                 elif period == "Weekly":
                     start_d = now - timedelta(days=7)
                     end_d = now
                 elif period == "Monthly":
                     start_d = now.replace(day=1)
                     end_d = now
        
    # Apply Filters
    df_filtered = df_raw.copy()
    # Normalize date
    df_filtered['date'] = pd.to_datetime(df_filtered['date']).dt.date
    
    if start_d and end_d:
        df_filtered = df_filtered[(df_filtered['date'] >= start_d) & (df_filtered['date'] <= end_d)]
    
    if sel_cat != "All":
        df_filtered = df_filtered[df_filtered['category'] == sel_cat]
    if sel_mode != "All":
        df_filtered = df_filtered[df_filtered['payment_method'] == sel_mode]
    
    # --- TABLE ---
    st.markdown(f"**Found {len(df_filtered)} records**")
    st.dataframe(
        df_filtered[['date', 'category', 'payment_method', 'amount', 'notes']].sort_values('date', ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "date": "Date",
            "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
            "category": "Category",
            "payment_method": "Payment Mode",
            "notes": "Description"
        }
    )
    

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅ Add Expense", key="led_nav_back", use_container_width=True):
            st.session_state.page = "transactions"
            st.rerun()
    with c2:
        if st.button("Analytics ➡", key="led_nav_next", type="primary", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
