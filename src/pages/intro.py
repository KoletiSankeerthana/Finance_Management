import streamlit as st
from src.utils.navigation import render_bottom_nav

def render_intro():
    # Hero Section
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 class='app-header-title'>EXPENSE TRACKER</h1>
        <p class='app-header-subtitle'>Professional Personal Finance Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # What is this Expense Tracker
    st.markdown("""
    ### 📊 What is this Expense Tracker?
    
    A comprehensive personal finance management tool designed to help you take control of your spending. 
    Track every transaction, set budgets, visualize your spending patterns, and make informed financial 
    decisions. Whether you're managing daily expenses, planning for the future, or simply wanting to 
    understand where your money goes, this tracker provides clear insights at a glance.
    """)
    
    st.markdown("---")
    
    # How to use (step-by-step)
    st.markdown("""
    ### 🚀 How to Use
    
    **Step 1: Add Expense**  
    Record your daily spending by entering the amount, category, payment method, and optional notes.
    
    **Step 2: View Expenses**  
    Navigate to the Expenses page to view all your transactions in a clean table. Filter by date, 
    category, or payment mode. Edit or delete any record as needed.
    
    **Step 3: Check Dashboard**  
    Get a quick overview of your weekly, monthly, and yearly spending totals. See your highest expense 
    and track your budget status with an easy-to-read progress indicator.
    
    **Step 4: Analyze Patterns**  
    Visit Analytics to see visual breakdowns of your spending by category and payment method. 
    Understand trends over time with interactive charts.
    
    **Step 5: Set Budgets**  
    Create spending limits for specific categories or set a global budget. The app will track your 
    spending against these limits and alert you when you're approaching or exceeding them.
    
    **Step 6: Manage Settings**  
    Update your account preferences, change your password, and manage your data from the Settings page.
    """)
    
    st.markdown("---")
    
    # Why it is useful
    st.markdown("""
    ### 💡 Why It's Useful
    
    **Budget Control**  
    Set clear spending limits and track your progress in real-time. Know exactly how much you have 
    left to spend in each category.
    
    **Spending Awareness**  
    Visual analytics help you identify spending patterns and make conscious decisions about where 
    your money goes.
    
    **Clean Financial Overview**  
    No clutter, no confusion. Get a clear, professional view of your finances with intuitive charts, 
    cards, and summaries.
    
    **Privacy & Security**  
    Your data stays with you. Secure authentication ensures only you can access your financial information.
    """)
    
    st.markdown("---")
    
    render_bottom_nav("welcome")
