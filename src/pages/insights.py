import streamlit as st
import pandas as pd
from datetime import datetime
from src.database.crud import load_transactions_df
from src.utils.formatting import format_currency

def render_insights():
    # --- Defensive Hardening (V12) ---
    if not st.session_state.get('authenticated'):
        st.warning("Please log in to access Financial Intelligence.")
        return
    if 'user_id' not in st.session_state:
        st.error("Session error: User ID missing. Please re-login.")
        return

    # V8 Hero Section
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; background: linear-gradient(90deg, #00b4d8, #0077b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Financial Intelligence</h1>
        <p style="color: #a4b0be; font-size: 1.05rem; margin-top: 5px;">AI-driven insights to optimize your saving habits.</p>
    </div>
    """, unsafe_allow_html=True)
    user_id = st.session_state.user_id
    
    # Load all historical data for insights
    df = load_transactions_df(user_id)
    
    if df.empty:
        st.info("FinancePro Insights will appear once you have some transaction history. Start adding your expenses to see patterns!")
        return
        
    # Rule-Based Intelligence Row
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    # 1. Budgeting Hero Card
    top_cat_data = df.groupby('category')['amount'].sum()
    top_cat = top_cat_data.idxmax()
    top_amt = top_cat_data.max()
    
    with col_a:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #a4b0be; margin-bottom: 5px;">Primary Expense</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #00b4d8;">{top_cat}</div>
            <div style="font-size: 0.85rem; color: #ff4b4b; margin-top: 5px;">🔥 {format_currency(top_amt)} Total</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Most Expensive Day Card
    df['day_name'] = df['date'].dt.day_name()
    day_spend = df.groupby('day_name')['amount'].sum()
    peak_day = day_spend.idxmax()
    
    with col_b:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #a4b0be; margin-bottom: 5px;">Peak Spending Day</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #f1c40f;">{peak_day}</div>
            <div style="font-size: 0.85rem; color: #a4b0be; margin-top: 5px;">📅 Consistent Spike Pattern</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Monthly Trajectory
    this_month_num = datetime.now().month
    last_month_num = (datetime.now().replace(day=1) - pd.Timedelta(days=1)).month
    
    tm_spend = df[df['date'].dt.month == this_month_num]['amount'].sum()
    lm_spend = df[df['date'].dt.month == last_month_num]['amount'].sum()
    
    st.markdown("### 📊 Monthly Trajectory")
    if lm_spend > 0:
        diff_pct = ((tm_spend - lm_spend) / lm_spend) * 100
        indicator = "up" if diff_pct > 0 else "down"
        color = "#ff4b4b" if diff_pct > 0 else "#00b894"
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid {color};">
            <div style="font-size: 1.1rem; font-weight: 600;">Spending is {indicator} by {abs(diff_pct):.1f}%</div>
            <p style="color: #a4b0be; margin: 10px 0;">Compared to last month ({format_currency(lm_spend)}), your current trajectory is {indicator}.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Baseline data not available for last month comparison.")

    # 4. Actionable Suggestions
    st.markdown("---")
    st.subheader("💡 Saving Suggestions")
    
    suggestions = {
        'Food & Dining': "Meal prepping on weekends can reduce 'Food & Dining' expenses by up to 25%.",
        'Transportation': "Consider public transport or carpooling for regular commutes to lower 'Transportation' costs.",
        'Shopping': "Wait 24 hours before any non-essential purchase to evaluate if it's a 'need' or a 'want'.",
        'Others': "Categorizing more expenses can provide better insights than leaving them as 'Others'."
    }
    
    suggestion = suggestions.get(top_cat, "Reviewing your monthly subscriptions is a quick way to find hidden savings.")
    st.success(f"**Pro Tip for {top_cat}**: {suggestion}")
