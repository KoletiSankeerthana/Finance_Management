import streamlit as st
import pandas as pd
from datetime import datetime
from src.database.crud import get_budgets, add_budget, get_categories, load_transactions_df, delete_budget
from src.utils.formatting import format_currency

def render_budgets():
    # --- Defensive Hardening (V12) ---
    if not st.session_state.get('authenticated'):
        st.warning("Please log in to access Budget Planning.")
        return
    if 'user_id' not in st.session_state:
        st.error("Session error: User ID missing. Please re-login.")
        return

    # V8 Hero Section
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; background: linear-gradient(90deg, #00b4d8, #0077b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Budget Planning</h1>
        <p style="color: #a4b0be; font-size: 1.05rem; margin-top: 5px;">Set goals and track your financial limits.</p>
    </div>
    """, unsafe_allow_html=True)
    user_id = st.session_state.user_id
    
    with st.expander("➕ Set New Budget"):
        with st.form("add_budget_form"):
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("Budget Amount", min_value=0.0, step=500.0)
                period = st.selectbox("Period", ["Monthly", "Yearly"])
            with col2:
                categories = get_categories(user_id)
                category_options = ["Total Monthly Spending"] + [c['name'] for c in categories]
                selected_cat = st.selectbox("Category", category_options)
                start_date = st.date_input("Start Date", datetime.now().date().replace(day=1))
            
            if st.form_submit_button("Set Budget", use_container_width=True):
                cat_val = selected_cat if selected_cat != "Total Monthly Spending" else None
                if add_budget(user_id, cat_val, amount, period, start_date):
                    st.success("Budget set successfully!")
                    st.rerun()

    st.markdown("---")
    
    budgets = get_budgets(user_id)
    if not budgets:
        st.info("No budgets defined yet. Set one above to track your limits!")
        return
    
    # Calculate current month's spending
    current_month_start = datetime.now().date().replace(day=1)
    df = load_transactions_df(user_id, filters={'start_date': current_month_start})
    
    for b in budgets:
        target_cat = b['category']
        
        if target_cat:
            # Category-specific budget
            spent = df[df['category'] == target_cat]['amount'].sum() if not df.empty else 0
            label = target_cat
        else:
            # Total budget
            spent = df['amount'].sum() if not df.empty else 0
            label = "Total Monthly Spending"
            
        percent = (spent / b['amount']) * 100 if b['amount'] > 0 else 0
        
        # V5 Executive Budget Card
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #fafafa; font-size: 1.2rem;">{label}</h3>
                <span style="font-size: 0.9rem; color: #8b949e;">{b['period']}</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: #{ 'ff4b4b' if percent >= 100 else '00d1b2' }; font-weight: 600;">
                    {format_currency(spent)}
                </span>
                <span style="color: #8b949e;">
                    Target: {format_currency(b['amount'])}
                </span>
            </div>
            
            <div style="width: 100%; height: 8px; background: #30363d; border-radius: 4px; overflow: hidden; margin-bottom: 10px;">
                <div style="width: {min(percent, 100)}%; height: 100%; background: { 'ff4b4b' if percent > 100 else '#f1c40f' if percent > 90 else '#00d1b2' };"></div>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.8rem; color: #8b949e;">{percent:.1f}% Used</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if percent >= 100:
             st.error(f"⚠️ Limit Exceeded!")
        
        # Delete Button (Streamlit button outside HTML)
        if st.button("Delete Budget", key=f"del_b_{b['id']}", use_container_width=True):
             delete_budget(b['id'], user_id)
             st.rerun()
