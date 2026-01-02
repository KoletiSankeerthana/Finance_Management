import streamlit as st
from src.utils.navigation import render_bottom_nav

def render_home():
    """
    Renders the Home/Welcome page with app introduction and usage guide.
    """
    st.markdown("""
    <div style="margin-bottom: 20px; text-align: center;">
        <h1 class='app-header-title'>WELCOME TO EXPENSE TRACKER</h1>
        <p class='app-header-subtitle'>Your Personal Finance Management Solution</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # What is this app about?
    st.markdown("###  What is Expense Tracker?")
    st.markdown("""
    **Expense Tracker** is a comprehensive personal finance management application designed to help you:
    - Track your daily expenses with ease
    - Visualize spending patterns through interactive analytics
    - Set and monitor budgets to stay financially disciplined
    - Manage custom categories for better organization
    - Gain insights into your financial health
    
    Built with simplicity and efficiency in mind, this app empowers you to take control of your finances.
    """)
    
    st.markdown("---")
    
    # What it contains
    st.markdown("###  Features & Pages")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Dashboard**  
        High-level overview of your spending with weekly, monthly, and yearly summaries.
        
        **➕ Add Expense**  
        Quick entry form to log your daily transactions with category selection.
        
        **🏷️ Categories**  
        Create and manage custom expense categories with emojis.
        """)
    
    with col2:
        st.markdown("""
        **💰 Budgets**  
        Set spending limits for categories and track your progress.
        
        **📈 Analytics**  
        Deep dive into your spending patterns with visual charts and insights.
        
        **⚙️ Settings**  
        Manage your account and application data.
        """)
    
    st.markdown("---")
    
    # How to use it
    st.markdown("### How to Use")
    st.markdown("""
    1. **Start with Categories**: Navigate to the **Categories** page and create your expense categories (e.g., Food, Transport, Entertainment).
    
    2. **Add Your Expenses**: Use the **Add Expense** page to log your daily spending. Select the category, enter the amount, and add a description.
    
    3. **Set Budgets**: Go to the **Budgets** page to set monthly or weekly spending limits for each category.
    
    4. **Monitor Your Dashboard**: Check the **Dashboard** regularly to see your spending summary and budget status.
    
    5. **Analyze Trends**: Visit the **Analytics** page to understand your spending patterns and make informed financial decisions.
    
    6. **Stay Organized**: Use the bottom navigation buttons (← Previous / Next →) to move between pages seamlessly.
    """)
    
    st.markdown("---")
    
    st.info("💡 **Tip**: Start by adding a few expenses and setting up your first budget to get the most out of this app!")
    
    render_bottom_nav("home")
