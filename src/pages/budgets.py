import streamlit as st
import pandas as pd
import time
from datetime import date, datetime, timedelta
from src.database.crud import add_budget, get_budgets, delete_budget, load_transactions_df
from src.utils.formatting import format_currency
from src.utils.constants import CATEGORIES, CATEGORY_ICONS

def render_budgets():
    if not st.session_state.get('authenticated'):
        st.warning("Please log in.")
        return
    
    user_id = st.session_state.user_id
    today = date.today()
    
    st.markdown(f"""
    <div style="margin-bottom: 20px; text-align: center;">
        <h1 class='app-header-title'>BUDGETS</h1>
        <p class='app-header-subtitle'>Set & Track Limits</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Create Budget Form ---
    st.markdown("### ➕ Set Budget")
    with st.container():
        with st.form("budget_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            # Options
            opts = ["Global (All Categories)"] + [f"{CATEGORY_ICONS.get(c, '')} {c}".strip() for c in CATEGORIES]
            cat_choice = c1.selectbox("Category", opts)
            amount = c2.number_input("Limit Amount (₹)", min_value=1.0, step=100.0)
            cycle = c3.selectbox("Cycle", ["Monthly", "Weekly"])
            
            if st.form_submit_button("Save Budget", type="primary"):
                # Parse Category
                if "Global" in cat_choice:
                    final_cat = "Global"
                else:
                    final_cat = cat_choice
                    for c in CATEGORIES:
                        if cat_choice.endswith(c):
                            final_cat = c
                            break
                            
                if add_budget(user_id, final_cat, amount, cycle, today):
                    st.success("Budget saved successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to save budget.")

    st.markdown("---")

    # --- Active Budgets ---
    st.markdown("### Budget Tracking")
    budgets = get_budgets(user_id)
    
    if budgets:
        tx_df = load_transactions_df(user_id)
        if not tx_df.empty:
            tx_df['date'] = pd.to_datetime(tx_df['date']).dt.date
            
        for b in budgets:
            limit = b['amount']
            cat = b['category']
            cycle = b['period']
            
            # Period Start
            if cycle == "Monthly":
                start_d = today.replace(day=1)
            else:
                curr_w_start = today - timedelta(days=today.weekday())
                start_d = max(curr_w_start, today.replace(day=1))
                
            # Calc Spent
            spent = 0.0
            if not tx_df.empty:
                sub = tx_df[tx_df['date'] >= start_d]
                if cat != "Global":
                    sub = sub[sub['category'] == cat]
                spent = sub['amount'].sum()
                
            remaining = limit - spent
            usage = min(spent / limit, 1.0) if limit > 0 else 0
            
            # Color
            if usage > 1.0: color = "#ef4444"
            elif usage > 0.8: color = "#ff9f43"
            else: color = "#10b981"
            
            # Display Card
            st.markdown(f"""
            <div class='metric-card' style='padding:15px; border-left:4px solid {color}; margin-bottom:10px;'>
                 <div style='display:flex; justify-content:space-between;'>
                     <h4 style='margin:0;'>{cat} ({cycle})</h4>
                     <strong style='color:{color};'>{format_currency(remaining)} Left</strong>
                 </div>
                 <div style='display:flex; justify-content:space-between; font-size:0.9rem; margin-top:5px;'>
                     <span>Spent: {format_currency(spent)}</span>
                     <span>Limit: {format_currency(limit)}</span>
                 </div>
                 <div style='background:rgba(255,255,255,0.1); height:8px; border-radius:4px; margin-top:5px;'>
                     <div style='background:{color}; width:{usage*100}%; height:100%; max-width:100%; border-radius:4px;'></div>
                 </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Delete logic outside card HTML
            if st.button(f"Delete ({cat})", key=f"del_b_{b['id']}"):
                delete_budget(b['id'], user_id)
                st.success("Deleted.")
                time.sleep(1)
                st.rerun()
                
    else:
        st.info("No active budgets found.")

    from src.utils.navigation import render_bottom_nav
    render_bottom_nav("budgets")
