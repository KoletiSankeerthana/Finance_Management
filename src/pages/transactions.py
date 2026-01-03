import streamlit as st
import pandas as pd
import time
from datetime import date, datetime, timedelta
from src.database.crud import add_transaction, load_transactions_df, delete_transaction, update_transaction
from src.utils.constants import CATEGORIES, PAYMENT_MODES
from src.utils.navigation import clean_category_icons, render_bottom_nav

def render_transactions():
    if not st.session_state.get('authenticated'):
        st.warning("Please log in.")
        return
    
    user_id = st.session_state.user_id
    today = date.today()

    st.markdown(f"""
    <div style="margin-bottom: 20px; text-align: center;">
        <h1 class='app-header-title'>EXPENSES</h1>
        <p class='app-header-subtitle'>Manage Your Spending</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Load Data & Categories ---
    df = load_transactions_df(user_id)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date']).dt.date
        df = clean_category_icons(df, user_id=user_id)
    
    from src.database.crud import get_categories, get_category_map
    cat_map = get_category_map(user_id)
    # List of names for filtering/processing
    all_cat_names = sorted(list(cat_map.keys()))
    # List of "Icon Name" for display
    display_cats = [f"{cat_map[c]} {c}".strip() for c in all_cat_names]
    
    # ==========================
    # 1. ACTIONS (COLLAPSIBLE)
    # ==========================
    st.markdown("### ⚡ Actions")
    
    # --- ADD EXPENSE ---
    # Manage expander state
    if "add_exp_expanded" not in st.session_state:
        st.session_state.add_exp_expanded = True

    with st.expander("▶ Add Expense", expanded=st.session_state.add_exp_expanded): 
        with st.form("add_txn_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            cat_display = c1.selectbox("Category", ["Select"] + display_cats)
            mode = c2.selectbox("Mode", ["Select"] + PAYMENT_MODES)
            amt = c1.number_input("Amount (₹)", min_value=0.0, value=0.0, step=1.0)
            txn_date = c2.date_input("Date", value=today)
            desc = st.text_input("Description (Optional)")
            
            submitted = st.form_submit_button("Save Expense", type="primary", use_container_width=True)
            if submitted:
                if cat_display == "Select" or mode == "Select":
                    st.error("Category and Payment Mode required.")
                elif amt <= 0:
                    st.error("Please enter a valid amount.")
                else:
                    # Extract pure category name
                    selected_cat_name = None
                    for name in all_cat_names:
                        if cat_display.endswith(name):
                            selected_cat_name = name
                            break
                    
                    if add_transaction(user_id, amt, selected_cat_name, mode, txn_date, desc):
                        st.success("Saved!")
                        # FORCE clear cache explicitly here as well
                        st.cache_data.clear()
                        # Collapse the form to show history
                        st.session_state.add_exp_expanded = False 
                        # Slightly longer delay to ensure cloud FS propagation
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("Error saving.")

    # --- EDIT/DELETE EXPENSE ---
    c_edit, c_del = st.columns(2)
    with c_edit:
        with st.expander("▶ Edit Expense"):
            e_cat_disp = st.selectbox("Category to Edit", ["Select"] + display_cats, key="edit_cat_disp")
            if e_cat_disp != "Select" and not df.empty:
                # Extract name
                e_cat = None
                for n in all_cat_names:
                    if e_cat_disp.endswith(n):
                        e_cat = n
                        break
                
                matches = df[df['category'] == e_cat].sort_values('date', ascending=False)
                if not matches.empty:
                    matches['label'] = matches.apply(lambda x: f"{x['date']} | ₹{x['amount']} | {x['notes'][:20]}...", axis=1)
                    sel_edit = st.selectbox("Select Transaction", matches['label'].tolist())
                    
                    row = matches[matches['label'] == sel_edit].iloc[0]
                    with st.form("edit_txn_form"):
                        u_cat = st.selectbox("New Category", display_cats, index=all_cat_names.index(row['category']))
                        u_mode = st.selectbox("New Mode", PAYMENT_MODES, index=PAYMENT_MODES.index(row['payment_method']))
                        u_amt = st.number_input("New Amount", value=float(row['amount']), min_value=0.1)
                        u_date = st.date_input("New Date", value=row['date'])
                        u_desc = st.text_input("New Description", value=row['notes'])
                        
                        if st.form_submit_button("Update"):
                            # Extract updated name
                            up_cat = None
                            for n in all_cat_names:
                                if u_cat.endswith(n):
                                    up_cat = n
                                    break
                            if update_transaction(int(row['id']), user_id, u_amt, up_cat, u_mode, u_date, u_desc):
                                st.success("Updated Successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to update transaction. Please try refreshing.")
                else:
                    st.info("No matches.")

    with c_del:
        with st.expander("▶ Delete Expense"):
            del_cat_disp = st.selectbox("Category", ["Select"] + display_cats, key="del_cat_simp")
            if del_cat_disp != "Select" and not df.empty:
                d_cat = None
                for n in all_cat_names:
                    if del_cat_disp.endswith(n):
                        d_cat = n
                        break
                
                mask = (df['category'] == d_cat)
                matches = df[mask].sort_values('date', ascending=False)
                if not matches.empty:
                    matches['label'] = matches.apply(lambda x: f"{x['date']} | ₹{x['amount']} | {x['notes'][:20]}...", axis=1)
                    target = st.selectbox("Select to Delete", matches['label'].tolist())
                    if st.button("Confirm Delete", type="primary", use_container_width=True):
                        if delete_transaction(int(matches[matches['label'] == target].iloc[0]['id']), user_id):
                            st.success("Deleted Successfully.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to delete. Please refresh.")
                else:
                    st.warning("Empty category.")
            
    st.markdown("---")

    # ==========================
    # 2. FILTERS
    # ==========================
    st.markdown("### 🔍 Search & Filter")
    with st.container():
        c1, c2, c3 = st.columns(3)
        # Default Filter: All
        period = c1.selectbox("Period", ["All", "Monthly", "Weekly", "Custom"], index=0)
        f_cat_disp = c2.selectbox("Category", ["All"] + display_cats, key="hist_cat")
        f_mode = c3.selectbox("Payment Mode", ["All"] + PAYMENT_MODES, key="hist_mode")
        
        start_date = None
        end_date = None
        
        if period == "Weekly":
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif period == "Monthly":
            start_date = today.replace(day=1)
            end_date = today
        elif period == "Custom":
            cd1, cd2 = st.columns(2)
            start_date = cd1.date_input("Start", value=today.replace(day=1))
            end_date = cd2.date_input("End", value=today)

    # ==========================
    # 3. HISTORY TABLE
    # ==========================
    view_df = df.copy()
    if not view_df.empty:
        # Resolve filter category name
        filter_cat_name = "All"
        if f_cat_disp != "All":
            for n in all_cat_names:
                if f_cat_disp.endswith(n):
                    filter_cat_name = n
                    break

        if start_date: view_df = view_df[view_df['date'] >= start_date]
        if end_date: view_df = view_df[view_df['date'] <= end_date]
        if filter_cat_name != "All": view_df = view_df[view_df['category'] == filter_cat_name]
        if f_mode != "All": view_df = view_df[view_df['payment_method'] == f_mode]
        
        view_df = view_df.sort_values(by='date', ascending=False)
        
        st.dataframe(
            view_df[['date', 'category', 'payment_method', 'amount', 'notes']],
            column_config={
                "date": st.column_config.DateColumn("Date", format="DD MMM"),
                "category": "Category",
                "payment_method": "Mode",
                "amount": st.column_config.NumberColumn("Amount", format="₹%.0f"),
                "notes": "Description"
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No records found.")
        
    render_bottom_nav("transactions")
