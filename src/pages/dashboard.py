import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.database.crud import load_transactions_df
from src.components.charts import plot_category_distribution
from src.utils.formatting import format_currency
import plotly.express as px

def render_dashboard():
    # --- Defensive Hardening (V12) ---
    if not st.session_state.get('authenticated'):
        st.warning("Please log in to access the Dashboard.")
        return
    if 'user_id' not in st.session_state:
        st.error("Session error: User ID missing. Please re-login.")
        return

    # --- V6 Hero Section & Period Selector ---
    col_hero, col_filter = st.columns([2, 1])
    with col_hero:
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <h1 style="margin: 0; font-size: 2.2rem; background: linear-gradient(90deg, #00b4d8, #0077b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Executive Dashboard</h1>
            <p style="color: #a4b0be; font-size: 1.05rem; margin-top: 5px;">Financial Overview for <strong>{st.session_state.gmail}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_filter:
        st.markdown("") # Spacing
        date_option = st.selectbox(
            "Reporting Period",
            ["Last 7 Days", "This Month", "Last 30 Days", "This Quarter", "This Year", "Custom Range"],
            key="dashboard_date_filter_v6"
        )

    user_id = st.session_state.user_id
    end_date = datetime.now().date()
    
    # Date Logic
    if date_option == "Last 7 Days":
        start_date = end_date - timedelta(days=7)
        prev_start = start_date - timedelta(days=7)
        prev_end = start_date - timedelta(days=1)
        period_label = "Weekly"
    elif date_option == "This Month":
        start_date = end_date.replace(day=1)
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end.replace(day=1)
        period_label = "Monthly"
    elif date_option == "Last 30 Days":
        start_date = end_date - timedelta(days=30)
        prev_start = start_date - timedelta(days=30)
        prev_end = start_date - timedelta(days=1)
        period_label = "Monthly"
    elif date_option == "This Quarter":
        quarter = (end_date.month - 1) // 3 + 1
        start_date = datetime(end_date.year, 3 * quarter - 2, 1).date()
        prev_end = start_date - timedelta(days=1)
        prev_quarter = (prev_end.month - 1) // 3 + 1
        prev_start = datetime(prev_end.year, 3 * prev_quarter - 2, 1).date()
        period_label = "Quarterly"
    elif date_option == "Custom Range":
        c_start, c_end = st.columns(2)
        start_date = c_start.date_input("From", end_date - timedelta(days=30))
        end_date = c_end.date_input("To", end_date)
        prev_start = start_date - timedelta(days=(end_date - start_date).days)
        prev_end = start_date - timedelta(days=1)
        period_label = "Custom"
    else: # This Year
        start_date = end_date.replace(month=1, day=1)
        prev_start = start_date.replace(year=start_date.year - 1)
        prev_end = start_date - timedelta(days=1)
        period_label = "Yearly"

    # Load Data (Cached V6)
    df_current = load_transactions_df(user_id, filters={'start_date': start_date, 'end_date': end_date})
    df_prev = load_transactions_df(user_id, filters={'start_date': prev_start, 'end_date': prev_end})
    
    # Executive Logic
    total_current = df_current['amount'].sum() if not df_current.empty else 0
    total_prev = df_prev['amount'].sum() if not df_prev.empty else 0
    
    if total_prev > 0:
        diff = total_current - total_prev
        diff_pct = (diff / total_prev) * 100
        indicator = "🔺" if diff > 0 else "🔻"
        color = "#ff4b4b" if diff > 0 else "#00b894" # Red if spend up, Green if spend down
        delta_str = f"{indicator} {abs(diff_pct):.1f}% vs Prev ({format_currency(abs(diff))})"
    else:
        diff_pct = 0
        color = "#a4b0be"
        delta_str = "No prior data"

    # Days in period for averaging
    days_in_period = (end_date - start_date).days + 1
    daily_avg = total_current / max(days_in_period, 1)

    # --- V6 Metrics Layout (Swap Request: Metrics First) ---
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #a4b0be; margin-bottom: 5px;">Total Expenses</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #f1f2f6;">{format_currency(total_current)}</div>
            <div style="font-size: 0.85rem; color: {color}; margin-top: 5px;">{delta_str}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #a4b0be; margin-bottom: 5px;">{period_label} Daily Avg</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #00b4d8;">{format_currency(daily_avg)}</div>
            <div style="font-size: 0.85rem; color: #a4b0be; margin-top: 5px;">Baseline Spending</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #a4b0be; margin-bottom: 5px;">Transactions</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #a29bfe;">{len(df_current)}</div>
            <div style="font-size: 0.85rem; color: #a4b0be; margin-top: 5px;">Volume Activity</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Charts & Analysis ---
    if df_current.empty:
        st.info("👋 No expenses yet for this period. Add your first expense to see insights!")
        if st.button("Add Expense Now (Redirect)"):
            st.session_state.page = "transactions" 
            st.rerun()
    else:
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.subheader("Spending Comparison")
            comp_df = pd.DataFrame({
                'Period': ['Previous', 'Current'],
                'Amount': [total_prev, total_current]
            })
            fig = px.bar(comp_df, x='Period', y='Amount', 
                         color='Period',
                         text_auto='.2s',
                         color_discrete_map={'Previous': '#4a4e69', 'Current': '#00b4d8'})
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)', 
                font_color='#a4b0be',
                bargap=0.85, # V13: Even thinner bars for executive look
                xaxis=dict(showgrid=False, title=None, tickfont=dict(family='Times New Roman', size=14)),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title=None, tickfont=dict(family='Times New Roman')),
                margin=dict(l=10, r=10, t=30, b=10),
                height=320,
                showlegend=False,
                modebar=dict(bgcolor='rgba(0,0,0,0)', color='#a4b0be', orientation='v')
            )
            fig.update_traces(marker_line_width=0, textfont_size=13, textfont_family='Times New Roman', textposition='outside')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': 'hover', 'modeBarButtonsToRemove': ['lasso2d', 'select2d'], 'displaylogo': False})
            
        with col_side:
            st.subheader("Top Categories")
            plot_category_distribution(df_current)
