import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.crud import load_transactions_df
from src.utils.formatting import format_currency

def render_analytics():
    # --- Defensive Hardening (V12) ---
    if not st.session_state.get('authenticated'):
        st.warning("Please log in to access Analytics.")
        return
    if 'user_id' not in st.session_state:
        st.error("Session error: User ID missing. Please re-login.")
        return

    # V8 Hero Section
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.2rem; background: linear-gradient(90deg, #00b4d8, #0077b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Financial Analytics</h1>
        <p style="color: #a4b0be; font-size: 1.05rem; margin-top: 5px;">Deep dive into your spending trends and distributions.</p>
    </div>
    """, unsafe_allow_html=True)
    user_id = st.session_state.user_id
    
    # Range selection (Professional)
    col1, col2 = st.columns([1, 1])
    with col1:
        start_date = st.date_input("From Date", pd.Timestamp.now().date() - pd.Timedelta(days=180))
    with col2:
        end_date = st.date_input("To Date", pd.Timestamp.now().date())
    
    # Load Data Safely
    filters = {'start_date': start_date, 'end_date': end_date}
    df = load_transactions_df(user_id, filters=filters)
    
    if df.empty:
        st.info("No data available for analytical processing in this period.")
        return
        
    # Pre-processing (V8 Clarity: explicit string formatting)
    df['month_year_sort'] = df['date'].dt.to_period('M')
    monthly_stats = df.groupby('month_year_sort')['amount'].sum().reset_index()
    monthly_stats['month_label'] = monthly_stats['month_year_sort'].dt.strftime('%b %Y')
    
    # --- Monthly Trend ---
    st.subheader("Monthly Spending Summary")
    
    # Sort chronologically
    monthly_stats = monthly_stats.sort_values('month_year_sort')
    
    fig = px.bar(monthly_stats, x='month_label', y='amount', 
                 text_auto='.2s',
                 color_discrete_sequence=['#00b4d8'])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        font_color='#a4b0be',
        bargap=0.85, # V13: Executive thin bars
        xaxis=dict(showgrid=False, title=None, tickfont=dict(family='Times New Roman', size=14)),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title=None, tickfont=dict(family='Times New Roman')),
        margin=dict(l=10, r=10, t=30, b=10),
        height=320,
        showlegend=False,
        modebar=dict(bgcolor='rgba(0,0,0,0)', color='#a4b0be', orientation='v')
    )
    fig.update_traces(marker_line_width=0, textfont_size=13, textfont_family='Times New Roman', textposition='outside')
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': 'hover', 'modeBarButtonsToRemove': ['lasso2d', 'select2d'], 'displaylogo': False})
    
    # --- Distribution Row ---
    st.markdown("---")
    m1, m2 = st.columns(2)
    with m1:
        st.subheader("Payment Method Split")
        pay_df = df.groupby('payment_method')['amount'].sum().reset_index()
        fig3 = px.pie(pay_df, values='amount', names='payment_method', hole=0.5,
                      color_discrete_sequence=px.colors.qualitative.Bold)
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#fafafa')
        st.plotly_chart(fig3, use_container_width=True)
        
    with m2:
        st.subheader("Executive Rankings")
        top_cats = df.groupby('category')['amount'].sum().sort_values(ascending=False).head(5)
        for cat, amt in top_cats.items():
            st.markdown(f"**{cat}**: {format_currency(amt)}")
            st.progress(min(amt / max(top_cats.max(), 1.0), 1.0))
