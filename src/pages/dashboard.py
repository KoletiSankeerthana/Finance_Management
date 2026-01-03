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

    # --- Header & Filter UI ---
    col_header, col_filter = st.columns([1, 1])
    
    with col_header:
        st.markdown(f"""
        <div style="text-align: left;">
            <h1 class='app-header-title'>DASHBOARD</h1>
            <p class='app-header-subtitle'>Financial Overview</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_filter:
        # Filter Logic
        filter_mode = st.selectbox("Period", ["Last Week", "Month Wise", "Year Wise", "Custom"], label_visibility="collapsed")
        
        start_date = None
        end_date = today # Default end is today
        
        if filter_mode == "Last Week":
            start_date = today - timedelta(days=7)
            
        elif filter_mode == "Month Wise":
            c_y, c_m = st.columns([1, 1])
            curr_year = today.year
            sel_year = c_y.selectbox("Year", range(curr_year, curr_year - 5, -1), label_visibility="collapsed")
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            curr_month_idx = today.month - 1
            if sel_year != curr_year: curr_month_idx = 0
            sel_month = c_m.selectbox("Month", months, index=curr_month_idx, label_visibility="collapsed")
            
            # Calculate range
            m_idx = months.index(sel_month) + 1
            start_date = date(sel_year, m_idx, 1)
            # End date is last day of month
            if m_idx == 12:
                end_date = date(sel_year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(sel_year, m_idx + 1, 1) - timedelta(days=1)
                
        elif filter_mode == "Year Wise":
            curr_year = today.year
            sel_year = st.selectbox("Year", range(curr_year, curr_year - 5, -1), label_visibility="collapsed")
            start_date = date(sel_year, 1, 1)
            end_date = date(sel_year, 12, 31)
            
        elif filter_mode == "Custom":
            c_s, c_e = st.columns(2)
            start_date = c_s.date_input("Start", value=today.replace(day=1), label_visibility="collapsed")
            end_date = c_e.date_input("End", value=today, label_visibility="collapsed")

    # --- Load Data & Apply Filter ---
    df = load_transactions_df(user_id)
    filtered_df = pd.DataFrame()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date']).dt.date
        from src.utils.navigation import clean_category_icons
        df = clean_category_icons(df, user_id=user_id)
        
        # Apply Filter
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        filtered_df = df[mask]
    
    # --- Calculate Dynamic Metrics ---
    total_spent = 0.0
    txn_count = 0
    highest_txn = 0.0
    daily_avg = 0.0
    
    if not filtered_df.empty:
        total_spent = filtered_df['amount'].sum()
        txn_count = len(filtered_df)
        highest_txn = filtered_df['amount'].max()
        
        # Avoid division by zero
        days_diff = (end_date - start_date).days + 1
        if days_diff > 0:
            daily_avg = total_spent / days_diff

    # --- Summary Cards (Dynamic) ---
    st.write('<style>div[data-testid="column"] {width: 100% !important; min-width: 150px !important;}</style>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    
    def card_html(label, sub_label, value):
        return f"""
        <div class="dashboard-card" style="background-color: #161b22; padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); min-height: 120px; display: flex; flex-direction: column; justify-content: center; overflow: hidden; transition: all 0.3s ease; cursor: pointer;">
            <p style="color: #a4b0be; font-size: 0.75rem; margin: 0; font-weight: 500; letter-spacing: 0.5px;">{label}</p>
            <p style="color: #008080; font-size: 0.7rem; margin: 2px 0;">{sub_label}</p>
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
        st.markdown(card_html("TOTAL OUTPUT", "Selected Period", format_currency(total_spent)), unsafe_allow_html=True)
    with c2:
        st.markdown(card_html("TRANSACTIONS", "Count", str(txn_count)), unsafe_allow_html=True)
    with c3:
        st.markdown(card_html("HIGHEST", "Single Spend", format_currency(highest_txn)), unsafe_allow_html=True)
    with c4:
        st.markdown(card_html("DAILY AVG", "Estimate", format_currency(daily_avg)), unsafe_allow_html=True)

    st.markdown("---")

    # --- Budget Status (Simplified for Dynamic View: Global Only or Total) ---
    # User might want to see Budget status regardless of filter, OR status for this period?
    # Standard logic: Budgets are Monthly or Weekly. It's hard to map "Custom" filter to Budget.
    # We will show the STANDARD current month/week budget status below independent of filter, 
    # OR we can show "Spend vs Limit" if the filter matches a budget period.
    # To keep it simple and useful: Show GLOBAL budget status for the Current Month as a reference.
    
    st.markdown("### 💰 Current Month Budget Status")
    
    # Recalculate strict monthly data for budget section
    start_month = today.replace(day=1)
    budgets = get_budgets(user_id)
    total_budget_limit = 0.0
    total_spent_in_budgets = 0.0
    
    # Get current month data from FULL df (not filtered_df)
    curr_month_df = df[df['date'] >= start_month] if not df.empty else pd.DataFrame()
    
    if budgets:
        for b in budgets:
            if b['period'] == 'Monthly': # Only track Monthly budgets in this view
                total_budget_limit += b['amount']
                if not curr_month_df.empty:
                    if b['category'] != "Global":
                        mask_b = (curr_month_df['category'] == b['category'])
                        total_spent_in_budgets += curr_month_df[mask_b]['amount'].sum()
                    else:
                         total_spent_in_budgets += curr_month_df['amount'].sum()
    
    # Only show if there IS a budget
    if total_budget_limit > 0:
        percent_actual = (total_spent_in_budgets / total_budget_limit * 100)
        remaining_budget = max(0, total_budget_limit - total_spent_in_budgets)
        
        bc1, bc2 = st.columns([3, 1])
        with bc1:
             st.markdown(f"""
            <div style="margin-top: 5px; background: rgba(255,255,255,0.1); border-radius: 6px; height: 20px; overflow: hidden;">
                <div style="width: {min(percent_actual, 100)}%; background: {'#ef4444' if percent_actual > 100 else '#10b981'}; height: 100%;"></div>
            </div>
            """, unsafe_allow_html=True)
        with bc2:
             st.write(f"**{percent_actual:.1f}%** ({format_currency(remaining_budget)} left)")
    else:
        st.caption("No Monthly Budgets set.")

    st.markdown("---")

    # --- Charts (Dynamic) ---
    st.markdown("### 📊 Spending Trend")
    
    if not filtered_df.empty:
        # Decide granularity: Daily if range < 60 days, else Monthly
        range_days = (end_date - start_date).days
        
        plot_df = filtered_df.copy()
        
        if range_days <= 60:
            # Daily View
            daily = plot_df.groupby('date', as_index=False)['amount'].sum()
            daily['date_str'] = daily['date'].apply(lambda d: d.strftime('%d %b'))
            fig = px.bar(daily, x='date_str', y='amount', color_discrete_sequence=['#ff9f43'])
        else:
            # Monthly View
            plot_df['month_year'] = pd.to_datetime(plot_df['date']).dt.strftime('%b %Y')
            # Sort chronologically logic required if spanning years, sticking to simple sort
            # For strict sort, convert to datetime
            monthly = plot_df.groupby('month_year', as_index=False)['amount'].sum()
            # Sort helper
            monthly['sort_key'] = pd.to_datetime(monthly['month_year'], format='%b %Y')
            monthly = monthly.sort_values('sort_key')
            
            fig = px.bar(monthly, x='month_year', y='amount', color_discrete_sequence=['#ff9f43'])

        fig.update_layout(
                bargap=0.8,
                height=350,
                xaxis_title=None, 
                yaxis_title="Amount",
                margin=dict(t=10, b=0, l=0, r=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No spending in this period.")

    render_bottom_nav("dashboard")
