import streamlit as st
from src.utils.constants import CATEGORY_ICONS

PAGES = {
    "welcome": "Home",
    "dashboard": "Dashboard",
    "transactions": "Expenses",
    "categories": "Categories",
    "analytics": "Analytics",
    "budgets": "Budgets",
    "settings": "Settings"
}

PAGE_ORDER = list(PAGES.keys())

def render_bottom_nav(current_page_key):
    """
    Renders Previous (<) and Next (>) buttons at the bottom of the page.
    Updates st.session_state.current_page and reruns.
    """
    st.markdown("---")
    try:
        idx = PAGE_ORDER.index(current_page_key)
    except ValueError:
        return

    cols = st.columns(2)
    
    # Previous Button
    if idx > 0:
        prev_key = PAGE_ORDER[idx - 1]
        prev_label = PAGES[prev_key]
        if cols[0].button(f"← {prev_label}", key=f"nav_prev_{current_page_key}", use_container_width=True):
            st.session_state.current_page = prev_label
            st.rerun()
            
    # Next Button
    if idx < len(PAGE_ORDER) - 1:
        next_key = PAGE_ORDER[idx + 1]
        next_label = PAGES[next_key]
        if cols[1].button(f"{next_label} →", key=f"nav_next_{current_page_key}", use_container_width=True):
            st.session_state.current_page = next_label
            st.rerun()

def clean_category_icons(df, user_id=None):
    """
    Removes icons from the 'category' column of a dataframe.
    If user_id is provided, it fetches specific icons for that user.
    """
    if df.empty or 'category' not in df.columns:
        return df
        
    # Build list of icons to strip
    icons_to_strip = set(CATEGORY_ICONS.values())
    
    if user_id:
        from src.database.crud import get_categories
        user_cats = get_categories(user_id)
        for c in user_cats:
            if c['emoji']:
                icons_to_strip.add(c['emoji'])
                
    def strip_icon(val):
        s_val = str(val)
        for icon in icons_to_strip:
            if icon and icon in s_val:
                s_val = s_val.replace(icon, "")
        return s_val.strip()
        
    df['category'] = df['category'].apply(strip_icon)
    return df
