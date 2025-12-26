import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.database.crud import add_transaction, load_transactions_df, get_categories, delete_transaction, get_category_map
from src.utils.formatting import format_currency

def render_transactions():
    # --- Defensive Hardening (V12) ---
    if not st.session_state.get('authenticated'):
        st.warning("Please log in to access Transactions.")
        return
    if 'user_id' not in st.session_state:
        st.error("Session error: User ID missing. Please re-login.")
        return

    # V13 Hero Section
    st.markdown(f"""
    <div style="margin-bottom: 25px;">
        <h1 style="margin: 0; font-size: 2.5rem; background: linear-gradient(90deg, #00b4d8, #0077b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Expense Ledger</h1>
        <p style="color: #a4b0be; font-size: 1.1rem; margin-top: 8px;">Detailed record of every financial movement across your accounts.</p>
    </div>
    """, unsafe_allow_html=True)
    
    user_id = st.session_state.user_id
    cat_emoji_map = get_category_map(user_id)
    
    # --- Form State Management ---
    if 'tx_amount' not in st.session_state: st.session_state.tx_amount = 0.0
    if 'tx_notes' not in st.session_state: st.session_state.tx_notes = ""
    
    with st.expander("➕ Log New Transaction", expanded=True):
        with st.form("add_tx_form_v13", clear_on_submit=False):
            # V13: Professional 3-column Form
            c1, c2, c3 = st.columns(3)
            with c1:
                amount = st.number_input("Amount", min_value=0.0, step=100.0, value=st.session_state.tx_amount, key="v13_amount")
                date = st.date_input("Date", value=datetime.now().date(), key="v13_date")
            with c2:
                categories = ["Select Category"] + list(cat_emoji_map.keys())
                category = st.selectbox("Category", categories, key="v13_category")
                payment_method = st.selectbox("Payment Method", ["Select Payment Method", "Cash", "Debit Card", "Credit Card", "UPI", "Net Banking", "Other"], key="v13_pay")
            with c3:
                notes = st.text_area("Observations / Notes", value=st.session_state.tx_notes, key="v13_notes", height=101)
            
            if st.form_submit_button("Authorize Expense", use_container_width=True):
                if amount <= 0:
                    st.error("Amount must be positive.")
                elif category == "Select Category":
                    st.error("Please assign a category.")
                elif payment_method == "Select Payment Method":
                    st.error("Please specify payment method.")
                else:
                    if add_transaction(user_id, amount, category, payment_method, date, notes):
                        st.success("Transaction recorded successfully.")
                        st.session_state.tx_amount = 0.0
                        st.session_state.tx_notes = ""
                        st.rerun()
                    else:
                        st.error("Database error occurred.")

    st.markdown("---")
    
    # --- Professional Filter Panel ---
    st.subheader("Advanced Filtering")
    
    if 'filter_cat' not in st.session_state: st.session_state.filter_cat = "Select Category"
    if 'filter_search' not in st.session_state: st.session_state.filter_search = ""
    
    fcol1, fcol2, fcol3 = st.columns([1, 1, 2])
    with fcol1:
        period_opt = st.selectbox("Timeframe", ["All Time", "Today", "This Month", "Last 3 Months", "Custom"])
    with fcol2:
        cat_filter = st.selectbox("Segment Filter", ["Select Category"] + list(cat_emoji_map.keys()), key="tx_filter_cat")
    with fcol3:
        search_input = st.text_input("🔍 Semantic Search", value=st.session_state.filter_search, placeholder="Search in notes...", key="tx_filter_search")
        st.session_state.filter_search = search_input

    # Date Logic
    start_date, end_date = None, datetime.now().date()
    if period_opt == "Today": start_date = end_date
    elif period_opt == "This Month": start_date = end_date.replace(day=1)
    elif period_opt == "Last 3 Months": start_date = end_date - timedelta(days=90)
    elif period_opt == "Custom":
        c_col1, c_col2 = st.columns(2)
        start_date = c_col1.date_input("Start", end_date - timedelta(days=30))
        end_date = c_col2.date_input("End", end_date)

    filters = {'start_date': start_date, 'end_date': end_date, 'search': search_input}
    df = load_transactions_df(user_id, filters=filters)
    if cat_filter != "Select Category":
        df = df[df['category'] == cat_filter]

    if df.empty:
        st.info("No ledger entries found for the selected criteria.")
        return
    
    # --- V13: Executive Table Structure ---
    st.markdown("""
    <div style="display: flex; font-weight: 700; font-size: 0.9rem; color: #00b4d8; padding: 15px; border-bottom: 2px solid var(--border); margin-bottom: 10px;">
        <div style="flex: 1;">Date</div>
        <div style="flex: 1.5;">Category</div>
        <div style="flex: 3;">Notes</div>
        <div style="flex: 1.2; text-align: right;">Amount</div>
        <div style="flex: 0.8; text-align: center;">Control</div>
    </div>
    """, unsafe_allow_html=True)
    
    for _, row in df.sort_values('date', ascending=False).iterrows():
        emoji = cat_emoji_map.get(row['category'], '🏷️')
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([1, 1.5, 3, 1.2, 0.8])
            c1.markdown(f"<p style='margin:0; font-family:var(--font-serif);'>{row['date'].strftime('%d %b %Y')}</p>", unsafe_allow_html=True)
            c2.markdown(f"<p style='margin:0; font-family:var(--font-serif);'>{emoji} {row['category']}</p>", unsafe_allow_html=True)
            c3.markdown(f"<p style='margin:0; font-family:var(--font-serif); color: #8b949e; overflow: hidden; text-overflow: ellipsis;'>{row['notes'] or '-'}</p>", unsafe_allow_html=True)
            c4.markdown(f"<p style='margin:0; font-family:var(--font-serif); font-weight: 700; text-align: right; color: #ff4b4b;'>{format_currency(row['amount'])}</p>", unsafe_allow_html=True)
            if c5.button("🗑️", key=f"del_v13_{row['id']}", use_container_width=True):
                if delete_transaction(row['id'], user_id):
                    st.rerun()
            st.markdown("<div style='border-bottom: 1px solid rgba(255,255,255,0.03); margin: 5px 0;'></div>", unsafe_allow_html=True)
