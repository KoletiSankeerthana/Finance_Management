import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
from src.database.crud import load_transactions_df, get_budgets
from src.utils.formatting import format_currency
from src.utils.navigation import render_bottom_nav

def render_dashboard():
    if not st.session_state.get('authenticated'):
        st.warning("Please log in.")
        return

    user_id = st.session_state.user_id
    today = date.today()

    st.markdown(f"""
    <div style="margin-bottom: 20px; text-align: center;">
        <h1 class='app-header-title'>DASHBOARD</h1>
        <p class='app-header-subtitle'>Financial Overview</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Manual Refresh ---
    rx1, rx2, rx3 = st.columns([4, 2, 4])
    with rx2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            from src.database.crud import _clear_cache
            _clear_cache()
            st.rerun()

    # --- Load Data ---
    df = load_transactions_df(user_id)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date']).dt.date
        from src.utils.navigation import clean_category_icons
        df = clean_category_icons(df, user_id=user_id)
    
    # --- Calculate Spend Metrics ---
    # Weekly: Sunday/Monday start clamped by month start to avoid Dec spillover
    curr_week_start = today - timedelta(days=today.weekday())
    start_week = max(curr_week_start, today.replace(day=1))
    
    start_month = today.replace(day=1)
    start_year = today.replace(month=1, day=1)
    
    val_week = 0.0
    val_month = 0.0
    val_year = 0.0
    val_highest = 0.0
    
    if not df.empty:
        val_week = df[df['date'] >= start_week]['amount'].sum()
        
        month_data = df[df['date'] >= start_month]
        val_month = month_data['amount'].sum()
        if not month_data.empty:
            val_highest = month_data['amount'].max()
            
        val_year = df[df['date'] >= start_year]['amount'].sum()

    # --- Summary Cards (4 cards) ---
    st.write('<style>div[data-testid="column"] {width: 100% !important; min-width: 150px !important;}</style>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    
    def card_html(label, date_info, value):
        return f"""
        <div class="dashboard-card" style="background-color: #161b22; padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); min-height: 120px; display: flex; flex-direction: column; justify-content: center; overflow: hidden; transition: all 0.3s ease; cursor: pointer;">
            <p style="color: #a4b0be; font-size: 0.75rem; margin: 0; font-weight: 500; letter-spacing: 0.5px;">{label}</p>
            <p style="color: #008080; font-size: 0.7rem; margin: 2px 0;">{date_info}</p>
            <h3 style="color: #fafafa; margin: 0; font-family: 'Times New Roman', serif; font-size: 1.3rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{value}</h3>
        </div>
        <style>
        .dashboard-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,128,128,0.3);
            border-color: rgba(0,128,128,0.5);
        }}
        </style>
        """

    with c1:
        st.markdown(card_html("MONTHLY", today.strftime('%B'), format_currency(val_month)), unsafe_allow_html=True)
    with c2:
        st.markdown(card_html("WEEKLY", f"{start_week.strftime('%d %b')} - Now", format_currency(val_week)), unsafe_allow_html=True)
    with c3:
        st.markdown(card_html("YEARLY", str(today.year), format_currency(val_year)), unsafe_allow_html=True)
    with c4:
        st.markdown(card_html("HIGHEST", "Single Txn (" + today.strftime('%B') + ")", format_currency(val_highest)), unsafe_allow_html=True)

    st.markdown("---")

    # --- Budget Status Section ---
    st.markdown("### 💰 Budget Status")
    
    budgets = get_budgets(user_id)
    total_budget_limit = 0.0
    total_spent_in_budgets = 0.0
    
    if budgets:
        for b in budgets:
            total_budget_limit += b['amount']
            b_start = start_month if b['period'] == "Monthly" else start_week
            
            if not df.empty:
                mask = (df['date'] >= b_start)
                if b['category'] != "Global":
                    mask &= (df['category'] == b['category'])
                total_spent_in_budgets += df[mask]['amount'].sum()
    
    # Calculate remaining (no negative)
    remaining_budget = max(0, total_budget_limit - total_spent_in_budgets)
    overspent_amount = max(0, total_spent_in_budgets - total_budget_limit)
    is_overspent = overspent_amount > 0
    
    # Progress bar calculation (Done BEFORE cards to fix NameError)
    percent_actual = (total_spent_in_budgets / total_budget_limit * 100) if total_budget_limit > 0 else 0

    # Display using Consistent Cards - ALWAYS 4 cards for layout consistency
    bc1, bc2, bc3, bc4 = st.columns(4)
    
    with bc1:
        st.markdown(card_html("TOTAL LIMIT", "ALL CATEGORIES", format_currency(total_budget_limit)), unsafe_allow_html=True)
    with bc2:
        st.markdown(card_html("TOTAL SPENT", f"{percent_actual:.1f}% Used", format_currency(total_spent_in_budgets)), unsafe_allow_html=True)
    with bc3:
        st.markdown(card_html("REMAINING", "Available Balance", format_currency(remaining_budget)), unsafe_allow_html=True)
    with bc4:
        # Always show Overspent card (requested by user for consistency)
        overspent_label = "Exceeded Limit" if is_overspent else "Within Budget"
        st.markdown(card_html("OVERSPENT", overspent_label, format_currency(overspent_amount)), unsafe_allow_html=True)

    # Progress bar with better styling
    st.markdown(f"""
    <div style="margin-top: 15px; background: rgba(255,255,255,0.1); border-radius: 6px; height: 10px; overflow: hidden;">
        <div style="width: {min(percent_actual, 100)}%; background: {'#ef4444' if is_overspent else '#10b981'}; height: 100%;"></div>
    </div>
    <p style="text-align: right; font-size: 0.8rem; color: #a4b0be; margin-top: 5px;">{percent_actual:.1f}% Utilized</p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # --- Charts ---
    st.markdown("### Daily Spending Trend")
    
    if not df.empty:
        # Filter for this month
        month_df = df[df['date'] >= start_month].copy()
        if not month_df.empty:
            # Aggregate by date correctly and convert to string for discrete axis
            daily = month_df.groupby('date', as_index=False)['amount'].sum()
            daily['date_str'] = daily['date'].apply(lambda d: d.strftime('%d %b'))
            
            fig = px.bar(daily, x='date_str', y='amount', 
                         color_discrete_sequence=['#ff9f43'])
            
            # Clean layout with thin bars and minimal gridlines
            fig.update_layout(
                bargap=0.9, # Even thinner bars
                height=350,
                xaxis_title=None, 
                yaxis_title="Amount",
                margin=dict(t=10, b=0, l=0, r=0),
                xaxis=dict(
                    showgrid=False,
                    type='category', 
                    tickmode='array',
                    tickvals=daily['date_str']
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)'
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No spending this month.")
    else:
        st.info("No data available.")
        
    render_bottom_nav("dashboard")
