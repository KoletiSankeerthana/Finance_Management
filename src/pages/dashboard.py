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
        # Filter Logic - Controls CHART ONLY
        filter_mode = st.selectbox("Period", ["Last Week", "Month Wise", "Year Wise", "Custom"], label_visibility="collapsed")
        
        start_date_chart = None
        end_date_chart = today 
        
        if filter_mode == "Last Week":
            start_date_chart = today - timedelta(days=7)
            
        elif filter_mode == "Month Wise":
            c_y, c_m = st.columns([1, 1])
            curr_year = today.year
            sel_year = c_y.selectbox("Year", range(curr_year, curr_year - 5, -1), label_visibility="collapsed")
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            curr_month_idx = today.month - 1
            if sel_year != curr_year: curr_month_idx = 0
            sel_month = c_m.selectbox("Month", months, index=curr_month_idx, label_visibility="collapsed")
            
            m_idx = months.index(sel_month) + 1
            start_date_chart = date(sel_year, m_idx, 1)
            if m_idx == 12:
                end_date_chart = date(sel_year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date_chart = date(sel_year, m_idx + 1, 1) - timedelta(days=1)
                
        elif filter_mode == "Year Wise":
            curr_year = today.year
            sel_year = st.selectbox("Year", range(curr_year, curr_year - 5, -1), label_visibility="collapsed")
            start_date_chart = date(sel_year, 1, 1)
            end_date_chart = date(sel_year, 12, 31)
            
        elif filter_mode == "Custom":
            c_s, c_e = st.columns(2)
            start_date_chart = c_s.date_input("Start", value=today.replace(day=1), label_visibility="collapsed")
            end_date_chart = c_e.date_input("End", value=today, label_visibility="collapsed")

    # --- Load FULL Data ---
    df = load_transactions_df(user_id)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date']).dt.date
        from src.utils.navigation import clean_category_icons
        df = clean_category_icons(df, user_id=user_id)

    # =========================================================
    # 1. STATIC CARDS (Current Status) - IGNORES FILTER
    # =========================================================
    
    # Calculate intervals
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
        st.markdown(card_html("MONTHLY", today.strftime('%B'), format_currency(val_month)), unsafe_allow_html=True)
    with c2:
        st.markdown(card_html("WEEKLY", f"{start_week.strftime('%d %b')} - Now", format_currency(val_week)), unsafe_allow_html=True)
    with c3:
        st.markdown(card_html("YEARLY", str(today.year), format_currency(val_year)), unsafe_allow_html=True)
    with c4:
        st.markdown(card_html("HIGHEST", "Single Txn (" + today.strftime('%B') + ")", format_currency(val_highest)), unsafe_allow_html=True)

    st.markdown("---")

    # =========================================================
    # 2. BUDGET STATUS (Current Month) - IGNORES FILTER
    # =========================================================
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
    percent_actual = (total_spent_in_budgets / total_budget_limit * 100) if total_budget_limit > 0 else 0

    bc1, bc2, bc3, bc4 = st.columns(4)
    with bc1:
        st.markdown(card_html("TOTAL LIMIT", "ALL CATEGORIES", format_currency(total_budget_limit)), unsafe_allow_html=True)
    with bc2:
        st.markdown(card_html("TOTAL SPENT", f"{percent_actual:.1f}% Used", format_currency(total_spent_in_budgets)), unsafe_allow_html=True)
    with bc3:
        st.markdown(card_html("REMAINING", "Available Balance", format_currency(remaining_budget)), unsafe_allow_html=True)
    with bc4:
        overspent_label = "Exceeded Limit" if is_overspent else "Within Budget"
        st.markdown(card_html("OVERSPENT", overspent_label, format_currency(overspent_amount)), unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top: 15px; background: rgba(255,255,255,0.1); border-radius: 6px; height: 10px; overflow: hidden;">
        <div style="width: {min(percent_actual, 100)}%; background: {'#ef4444' if is_overspent else '#10b981'}; height: 100%;"></div>
    </div>
    <p style="text-align: right; font-size: 0.8rem; color: #a4b0be; margin-top: 5px;">{percent_actual:.1f}% Utilized</p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # =========================================================
    # 3. DYNAMIC CHARTS - USES FILTER
    # =========================================================
    # Create filtered DF for Chart
    chart_df = pd.DataFrame()
    if not df.empty:
        mask = (df['date'] >= start_date_chart) & (df['date'] <= end_date_chart)
        chart_df = df[mask]
    
    # Metrics for Filtered Data
    txn_count = len(chart_df)
    
    # Header with Count
    st.markdown(f"### 📊 Spending Trend <span style='font-size:1rem; font-weight:normal; color:#a4b0be; margin-left:10px;'>({txn_count} Transactions)</span>", unsafe_allow_html=True)
    
    if not chart_df.empty:
        range_days = (end_date_chart - start_date_chart).days
        plot_df = chart_df.copy()
        
        if range_days <= 60:
            # Daily View
            daily = plot_df.groupby('date', as_index=False)['amount'].sum()
            daily['date_str'] = daily['date'].apply(lambda d: d.strftime('%d %b'))
            fig = px.bar(daily, x='date_str', y='amount', color_discrete_sequence=['#ff9f43'])
        else:
            # Monthly View
            plot_df['month_year'] = pd.to_datetime(plot_df['date']).dt.strftime('%b %Y')
            monthly = plot_df.groupby('month_year', as_index=False)['amount'].sum()
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
