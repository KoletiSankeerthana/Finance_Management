import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
from src.database.crud import load_transactions_df
from src.utils.navigation import clean_category_icons, render_bottom_nav

def render_analytics():
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
            <h1 class='app-header-title'>ANALYTICS</h1>
            <p class='app-header-subtitle'>Spending Insights</p>
        </div>
        """, unsafe_allow_html=True)

    with col_filter:
        # Filter Logic
        filter_mode = st.selectbox("Period", ["Last Week", "Month Wise", "Year Wise", "Custom"], label_visibility="collapsed", key="analytics_filter")
        
        start_date = None
        end_date = today # Default end is today
        
        if filter_mode == "Last Week":
            start_date = today - timedelta(days=7)
            
        elif filter_mode == "Month Wise":
            c_y, c_m = st.columns([1, 1])
            curr_year = today.year
            sel_year = c_y.selectbox("Year", range(curr_year, curr_year - 5, -1), label_visibility="collapsed", key="an_year")
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            curr_month_idx = today.month - 1
            if sel_year != curr_year: curr_month_idx = 0
            sel_month = c_m.selectbox("Month", months, index=curr_month_idx, label_visibility="collapsed", key="an_month")
            
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
            sel_year = st.selectbox("Year", range(curr_year, curr_year - 5, -1), label_visibility="collapsed", key="an_year_wise")
            start_date = date(sel_year, 1, 1)
            end_date = date(sel_year, 12, 31)
            
        elif filter_mode == "Custom":
            c_s, c_e = st.columns(2)
            start_date = c_s.date_input("Start", value=today.replace(day=1), label_visibility="collapsed", key="an_start")
            end_date = c_e.date_input("End", value=today, label_visibility="collapsed", key="an_end")

    # --- Load Data & Apply Filter ---
    df = load_transactions_df(user_id)
    
    if df.empty:
        st.info("No data available.")
        render_bottom_nav("analytics")
        return

    # Fix Date & Clean Icons
    df['date'] = pd.to_datetime(df['date'])
    df = clean_category_icons(df, user_id=user_id)
    
    # Filter Data
    mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
    filtered_df = df[mask]
    
    if filtered_df.empty:
        st.info(f"No transactions found for the selected period ({filter_mode}).")
    else:
        # --- Charts ---
        c1, c2 = st.columns(2)
        
        # 1. Category Distribution
        with c1:
            st.markdown("#### Category Distribution")
            cat_df = filtered_df.groupby('category')['amount'].sum().reset_index()
            fig1 = px.pie(cat_df, values='amount', names='category', 
                        color_discrete_sequence=px.colors.qualitative.Pastel)
            fig1.update_layout(showlegend=True, height=350, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig1, use_container_width=True)
    
        # 2. Payment Method
        with c2:
            st.markdown("#### Payment Mode Split")
            pay_df = filtered_df.groupby('payment_method')['amount'].sum().reset_index()
            fig2 = px.pie(pay_df, values='amount', names='payment_method',
                        color_discrete_sequence=px.colors.sequential.Teal)
            fig2.update_layout(showlegend=True, height=350, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig2, use_container_width=True)
            
        # 3. Dynamic Trend (Daily vs Monthly based on Range)
        st.markdown("#### 📊 Spending Trend")
        
        range_days = (end_date - start_date).days
        plot_df = filtered_df.copy()
        
        if range_days <= 60:
            # Daily View
            daily = plot_df.groupby(plot_df['date'].dt.date)['amount'].sum().reset_index()
            daily.columns = ['date', 'amount'] # explicit rename
            daily['date_str'] = pd.to_datetime(daily['date']).apply(lambda d: d.strftime('%d %b'))
            fig3 = px.bar(daily, x='date_str', y='amount', color_discrete_sequence=['#008080'])
        else:
            # Monthly View
            plot_df['month_year'] = plot_df['date'].dt.strftime('%b %Y')
            monthly = plot_df.groupby('month_year', as_index=False)['amount'].sum()
            monthly['sort_key'] = pd.to_datetime(monthly['month_year'], format='%b %Y')
            monthly = monthly.sort_values('sort_key')
            fig3 = px.bar(monthly, x='month_year', y='amount', color_discrete_sequence=['#008080'])

        fig3.update_layout(height=300, bargap=0.6, xaxis_title=None, yaxis_title="Amount") # Thin bars
        st.plotly_chart(fig3, use_container_width=True)
        
    render_bottom_nav("analytics")
