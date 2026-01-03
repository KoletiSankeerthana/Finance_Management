from datetime import datetime
import streamlit as st
from src.utils.constants import CATEGORY_ICONS, APP_TITLE, APP_SUBTITLE
from src.auth.session import logout_user

PAGES = {
    "home": "Home",
    "dashboard": "Dashboard",
    "transactions": "Add Expense",
    "categories": "Categories",
    "budgets": "Budgets",
    "analytics": "Analytics",
    "settings": "Settings"
}

PAGE_ORDER = list(PAGES.keys())

NAV_CONFIG = {
    "Home": {"icon": "🏠", "render": "render_home", "import": "src.pages.home"},
    "Dashboard": {"icon": "📊", "render": "render_dashboard", "import": "src.pages.dashboard"},
    "Add Expense": {"icon": "➕", "render": "render_transactions", "import": "src.pages.transactions"},
    "Categories": {"icon": "🏷️", "render": "render_categories", "import": "src.pages.categories"},
    "Budgets": {"icon": "💰", "render": "render_budgets", "import": "src.pages.budgets"},
    "Analytics": {"icon": "📈", "render": "render_analytics", "import": "src.pages.analytics"},
    "Settings": {"icon": "⚙️", "render": "render_settings", "import": "src.pages.settings"}
}

def render_sidebar():
    """
    Renders a responsive, persistent sidebar.
    """
    expanded = st.session_state.get('sidebar_expanded', True)
    
    # CSS for Sidebar Width control and responsiveness
    sidebar_width = "280px" if expanded else "0px"
    st.markdown(f"""
        <style>
        /* Universal SideBar: 0px or 280px everywhere */
        [data-testid="stSidebar"] {{
            min-width: {sidebar_width} !important;
            max-width: {sidebar_width} !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        /* Force main content to expand when sidebar is width 0 */
        {f"[data-testid='stMain'] {{ margin-left: 0 !important; padding-left: 1rem !important; }}" if not expanded else ""}
        
        [data-testid="stSidebar"] {{
            background-color: #050505 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            overflow: visible !important; /* Critical to show the fixed toggle */
        }}
        
        [data-testid="stSidebarNav"] {{ display: none; }} /* Hide default nav */
        
        /* Persistent Toggle Button Styling - Always Fixed at top-left */
        .sidebar-toggle-btn {{
            position: fixed !important;
            top: 15px !important;
            left: 15px !important;
            z-index: 99999 !important; /* Top of everything */
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}
        .sidebar-toggle-btn button {{
            background: rgba(0, 128, 128, 0.2) !important; /* Low-profile teal tint */
            backdrop-filter: blur(5px);
            border: 1px solid rgba(0, 128, 128, 0.3) !important;
            color: var(--primary) !important;
            font-size: 1.2rem !important;
            padding: 0 !important;
            min-height: 0 !important;
            width: 32px !important;
            height: 32px !important;
            border-radius: 8px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        .sidebar-toggle-btn button:hover {{
            background: var(--primary) !important;
            color: white !important;
            transform: scale(1.05);
        }}

        /* Hide content when collapsed */
        {f" div[data-testid='stSidebar'] .sidebar-text-container, div[data-testid='stSidebar'] .username-text, div[data-testid='stSidebar'] hr, div[data-testid='stSidebar'] .stButton, div[data-testid='stSidebar'] .stCaption, div[data-testid='stSidebar'] p {{ opacity: 0 !important; pointer-events: none !important; }} " if not expanded else ""}
        
        /* Special case: hide everything but allow the toggle wrapper back */
        .sidebar-toggle-btn {{ opacity: 1 !important; pointer-events: auto !important; }}

        /* Prevent character stacking */
        [data-testid="stSidebar"] * {{
            word-break: keep-all !important;
            overflow-wrap: normal !important;
            white-space: nowrap !important;
        }}
        
        /* Hide native Streamlit header button */
        button[kind="header"] {{ display: none !important; }}
        </style>
        <script>
        function hideNativeElements() {{
            const doc = window.parent.document;
            const buttons = doc.querySelectorAll('button');
            buttons.forEach(btn => {{
                if (btn.getAttribute("kind") === "header") {{
                    btn.style.display = 'none';
                }}
            }});
        }}
        hideNativeElements();
        setTimeout(hideNativeElements, 100);
        setInterval(hideNativeElements, 1000); 
        </script>

    """, unsafe_allow_html=True)

    with st.sidebar:
        # 1. Persistent Arrow Toggle (Fix for all devices)
        st.markdown('<div class="sidebar-toggle-btn">', unsafe_allow_html=True)
        toggle_icon = "«" if expanded else "»"
        if st.button(toggle_icon, key="sidebar_toggle_persistent"):
            st.session_state.sidebar_expanded = not expanded
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        if expanded:
            st.markdown(f"""
            <div class='sidebar-text-container' style='padding: 0 0 15px 10px; text-align: left;'>
                <p style='font-size:1.2rem; font-weight:bold; color:var(--primary); margin:0;'>{APP_TITLE}</p>
                <p style='font-size: 0.7rem; color:var(--text-muted); margin:0;'>{APP_SUBTITLE}</p>
            </div>
            """, unsafe_allow_html=True)
            # Display username
            username = st.session_state.get('username', "User")
            st.markdown(f"<p class='username-text' style='margin-left: 10px;'>👤 **{username}**</p>", unsafe_allow_html=True)
            st.markdown("---")
        else:
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # Navigation Menu
        for label, config in NAV_CONFIG.items():
            is_active = st.session_state.current_page == label
            icon = config.get('icon', '')
            
            if expanded:
                btn_label = f"{icon}  {label}"
            else:
                btn_label = icon if icon else label[:1]
            
            if st.button(
                btn_label, 
                key=f"nav_{label}", 
                use_container_width=True,
                type="primary" # All buttons Green as requested
            ):
                st.session_state.current_page = label
                st.rerun()

        st.markdown("---")
        # Use a div to allow CSS targeting for text part if needed, 
        # but for buttons we rely on the global div[data-testid="stSidebar"] button div p rule
        logout_btn_label = "🔓 Logout" if expanded else "🔓"
        if st.button(logout_btn_label, use_container_width=True, key="sidebar_logout"):
            logout_user()

def render_bottom_nav(current_page_key):
    """
    Renders Previous (<) and Next (>) buttons at the bottom of the page.
    """
    st.markdown("---")
    try:
        idx = PAGE_ORDER.index(current_page_key)
    except ValueError:
        return

    # Left and Right corner positioning (as requested)
    cols = st.columns([3, 4, 3])
    
    # Previous Button (Left corner)
    if idx > 0:
        prev_key = PAGE_ORDER[idx - 1]
        prev_label = PAGES[prev_key]
        if cols[0].button(f"← {prev_label}", key=f"nav_prev_{current_page_key}", use_container_width=True):
            st.session_state.current_page = prev_label
            st.rerun()
            
    # Next Button (Right corner)
    if idx < len(PAGE_ORDER) - 1:
        next_key = PAGE_ORDER[idx + 1]
        next_label = PAGES[next_key]
        if cols[2].button(f"{next_label} →", key=f"nav_next_{current_page_key}", use_container_width=True):
            st.session_state.current_page = next_label
            st.rerun()

def clean_category_icons(df, user_id=None):
    """
    Removes icons from the 'category' column of a dataframe.
    """
    if df.empty or 'category' not in df.columns:
        return df
        
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
