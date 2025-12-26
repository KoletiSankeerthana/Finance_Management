import streamlit as st
import pandas as pd
import plotly.express as px

def plot_category_distribution(df):
    if df.empty or 'category' not in df.columns or 'amount' not in df.columns:
        st.info("Insufficient data for category breakdown")
        return
    
    cat_spend = df.groupby('category')['amount'].sum().reset_index()
    
    fig = px.pie(cat_spend, values='amount', names='category', 
                 hole=0.75, # V9: thinner ring
                 color_discrete_sequence=px.colors.qualitative.G10)
    
    fig.update_layout(
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#fafafa',
        margin=dict(l=20, r=20, t=30, b=20),
        height=350, # Increased height for better visibility
        # V10: Modebar positioning (Top Right)
        modebar=dict(bgcolor='rgba(0,0,0,0)', color='#a4b0be', orientation='v')
    )
    # Ensure circularity by setting traces to fixed domain if needed, 
    # but height/width balance usually handles it in Streamlit.
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': 'hover', 'modeBarButtonsToRemove': ['lasso2d', 'select2d'], 'displaylogo': False})
