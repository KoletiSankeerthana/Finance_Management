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
    sidebar_width = "280px" if expanded else "80px"
    st.markdown(f"""
        <style>
        [data-testid="stSidebar"] {{
            min-width: {sidebar_width} !important;
            max-width: {sidebar_width} !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            background-color: #050505 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }}
        [data-testid="stSidebarNav"] {{ display: none; }} /* Hide default nav */
        
        /* Prevent ANY vertical character stacking */
        [data-testid="stSidebar"] * {{
            word-break: keep-all !important;
            overflow-wrap: normal !important;
            white-space: nowrap !important;
        }}
        
        /* Sidebar item text stays in one line with ellipsis */
        div[data-testid="stSidebar"] button div p {{
            text-overflow: ellipsis !important;
            display: block !important;
            font-size: 0.9rem !important;
        }}

        /* Responsive Breakpoints: Single Clean Block */
        @media (max-width: 1024px) {{
            /* Tablet transition: Force collapse to icons visually */
            [data-testid="stSidebar"] {{
                min-width: 80px !important;
                max-width: 80px !important;
            }}
            
            /* Show ONLY icon: set a narrow width and center it */
            [data-testid="stSidebar"] button div p {{
                width: 32px !important; 
                overflow: hidden !important;
                text-align: center !important;
                margin: 0 auto !important;
                font-size: 1.25rem !important;
            }}
            
            /* Hide title and username text on small screens */
            .sidebar-text-container, .username-text, .nav-text {{
                display: none !important;
            }}
        }}
        
        /* Hide default Streamlit sidebar toggle */
        button[kind="header"] {{ display: none !important; }}
        </style>
        
        <!-- REMOVED CUSTOM HAMBURGER ("3 lines") and HIDDEN NATIVE CHEVRON ("<") AS REQUESTED -->
        <!-- The sidebar will now rely on its expanded state and window width -->
        
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Internal State Management Buttons (HIDDEN via container class)
        # These manage the actual python state.
        
        # Force HIDE the internal proxy buttons using JavaScript (More robust than CSS :has)
        st.markdown("""
        <script>
        function hideArrows() {
            const doc = window.parent.document;
            const buttons = doc.querySelectorAll('button');
            
            buttons.forEach(btn => {
                // 1. Hide Native Sidebar Close Button (Chevron)
                if (btn.getAttribute("kind") === "header") {
                    btn.style.display = 'none';
                }
                
                // 2. Hide our Internal Proxy Buttons (« and »)
                // We check innerText carefully
                if (btn.innerText.includes("«") || btn.innerText.includes("»")) {
                    btn.style.display = 'none';
                    // Ensure they are still clickable by JS but invisible layout-wise
                    btn.style.visibility = 'hidden';
                    btn.style.position = 'absolute';
                    btn.style.width = '0px';
                    btn.style.height = '0px';
                }
            });
        }
        
        // Run immediately and on frequent intervals to catch re-renders
        hideArrows();
        setTimeout(hideArrows, 100);
        setTimeout(hideArrows, 500);
        setInterval(hideArrows, 1000); // Polling ensures it stays hidden if Streamlit re-mounts
        </script>
        <style>
        /* Fallback CSS for native header */
        [data-testid="stSidebar"] button[kind="header"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)

        with st.container():
             # Inject CSS to hide this specific container content
            st.markdown('<div class="hidden-toggle-container">', unsafe_allow_html=True)
            if expanded:
                 if st.button("«", key="sidebar_toggle_collapse"):
                    st.session_state.sidebar_expanded = False
                    st.rerun()
            else:
                 if st.button("»", key="sidebar_toggle_expand"):
                    st.session_state.sidebar_expanded = True
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
