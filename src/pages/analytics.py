import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.crud import load_transactions_df
from src.utils.navigation import clean_category_icons, render_bottom_nav

def render_analytics():
    if not st.session_state.get('authenticated'):
        st.warning("Please log in.")
        return
    
    user_id = st.session_state.user_id
    
    st.markdown(f"""
    <div style="margin-bottom: 20px; text-align: center;">
        <h1 class='app-header-title'>ANALYTICS</h1>
        <p class='app-header-subtitle'>Spending Insights</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Load Data ---
    df = load_transactions_df(user_id)
    
    if df.empty:
        st.info("No data available.")
        render_bottom_nav("analytics")
        return

    # Fix Date & Clean Icons
    df['date'] = pd.to_datetime(df['date'])
    df = clean_category_icons(df, user_id=user_id)

    # --- Charts ---
    c1, c2 = st.columns(2)
    
    # 1. Category Distribution
    with c1:
        st.markdown("#### Category Distribution")
        cat_df = df.groupby('category')['amount'].sum().reset_index()
        fig1 = px.pie(cat_df, values='amount', names='category', 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig1.update_layout(showlegend=True, height=350, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig1, use_container_width=True)

    # 2. Payment Method
    with c2:
        st.markdown("#### Payment Mode Split")
        pay_df = df.groupby('payment_method')['amount'].sum().reset_index()
        fig2 = px.pie(pay_df, values='amount', names='payment_method',
                     color_discrete_sequence=px.colors.sequential.Teal)
        fig2.update_layout(showlegend=True, height=350, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig2, use_container_width=True)
        
    # 3. Monthly Trend (Bar)
    st.markdown("#### 📅 Monthly Trend")
    df['month_year'] = df['date'].dt.strftime('%b %Y')
    
    monthly = df.groupby('month_year')['amount'].sum().reset_index()
    
    fig3 = px.bar(monthly, x='month_year', y='amount', color_discrete_sequence=['#008080'])
    fig3.update_layout(height=300, bargap=0.6, xaxis_title=None, yaxis_title="Amount") # Thin bars
    st.plotly_chart(fig3, use_container_width=True)
    
    render_bottom_nav("analytics")
