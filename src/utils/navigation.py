import streamlit as st
from src.utils.constants import CATEGORY_ICONS, APP_TITLE, APP_SUBTITLE
from src.auth.session import logout_user

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

NAV_CONFIG = {
    "Dashboard": {"icon": "📊", "render": "render_dashboard", "import": "src.pages.dashboard"},
    "Analytics": {"icon": "📈", "render": "render_analytics", "import": "src.pages.analytics"},
    "Add Expense": {"icon": "📄", "render": "render_transactions", "import": "src.pages.transactions"},
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
        
        /* Prevent vertical wrapping on small sidebars */
        .stButton button {{ 
            white-space: nowrap !important; 
            overflow: hidden !important; 
            text-align: left !important;
            padding-left: 15px !important;
        }}
        
        /* Sidebar item text stays in one line */
        div[data-testid="stSidebar"] button div p {{
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            display: block !important;
        }}
        
        /* Hide default Streamlit sidebar toggle */
        button[kind="header"] {{ display: none !important; }}

        /* Responsive Breakpoints */
        @media (max-width: 1024px) {{
            /* Tablet: Force collapse to icons */
            [data-testid="stSidebar"] {{
                min-width: 80px !important;
                max-width: 80px !important;
            }}
            [data-testid="stSidebar"] .nav-text {{ display: none !important; }}
        }}

        @media (max-width: 768px) {{
            /* Handled by Streamlit mobile overlay */
        }}
        </style>
    """, unsafe_allow_html=True)

    # --- JAVASCRIPT PROXY PATTERN FOR GLOBAL TOGGLE ---
    # The user wants ONLY the hamburger to be visible.
    # We keep the "Internal Buttons" (« / ») to manage state, but HIDE them with CSS.
    # The Hamburger then "clicks" them via JS.
    
    st.markdown("""
        <style>
        /* Hide the internal expand/collapse buttons visually */
        div[data-testid="stSidebar"] button[kind="secondary"], 
        div[data-testid="stSidebar"] button[kind="base"] {
            /* We carefully only hide the arrow buttons if we can target them specifically. 
               Since they use specific keys, we can look for their structure or just use the container class below.
               Actually, we will wrap them in a container that we hide. */
        }
        
        .hidden-toggle-container {
            display: none;
        }
        
        /* Custom Hamburger Styling (Robust Fixed Position) */
        .custom-hamburger {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 9999999;
            background-color: #0E1117;
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            display: flex;
            align-items: center;
            justify_content: center;
            transition: all 0.2s ease;
        }
        .custom-hamburger:hover {
            background-color: #262730;
            transform: scale(1.05);
        }
        
        /* Ensure sidebar top padding for the hamburger overlap */
        section[data-testid="stSidebar"] > div {
            padding-top: 60px;
        }
        </style>
        
        <script>
        function toggleSidebar() {
            // PROXY LOGIC: Find the hidden internal buttons and click them.
            const buttons = Array.from(window.parent.document.querySelectorAll('button'));
            
            // 1. Try to find the "Collapse" («) or "Expand" (») buttons by their text
            // Note: We wrapped them in a generic button call, Streamlit renders them as buttons with text.
            let targetBtn = buttons.find(b => b.innerText.includes("«") || b.innerText.includes("»"));
            
            if (targetBtn) {
                targetBtn.click();
            } else {
                // 2. Fallback: If for some reason internal buttons aren't found (e.g. mobile overlay),
                // trigger Streamlit's native sidebar toggle.
                const headerBtn = window.parent.document.querySelector('button[kind="header"]');
                if (headerBtn) headerBtn.click();
            }
        }
        </script>
        
        <div class="custom-hamburger" onclick="toggleSidebar()" title="Toggle Sidebar">
            <span style="font-size: 1.2rem; font-weight: bold;">☰</span>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Internal State Management Buttons (HIDDEN via container class)
        # These manage the actual python state.
        with st.container():
            # Inject CSS to hide this specific container content
            st.markdown('<div class="hidden-toggle-container">', unsafe_allow_html=True)
            # Force HIDE the internal proxy buttons using strict CSS targeting by title attribute
            st.markdown("""
            <style>
            /* Hide the native Streamlit sidebar close button (The '<' chevron) */
            [data-testid="stSidebar"] button[kind="header"] {
                display: none !important;
            }
            
            /* Hide our custom proxy buttons (The Green '«' / '»') */
            /* We use visibility:hidden so they stay in DOM for JS to click */
            button[title="Collapse Sidebar"], button[title="Expand Sidebar"] {
                visibility: hidden !important;
                position: absolute !important;
                width: 1px !important;
                height: 1px !important;
                padding: 0 !important;
                margin: -1px !important;
                overflow: hidden !important;
                clip: rect(0,0,0,0) !important;
                border: 0 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if expanded:
                 if st.button("«", key="sidebar_toggle_collapse", help="Collapse Sidebar"):
                    st.session_state.sidebar_expanded = False
                    st.rerun()
            else:
                 if st.button("»", key="sidebar_toggle_expand", help="Expand Sidebar"):
                    st.session_state.sidebar_expanded = True
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        if expanded:
            st.markdown(f"""
            <div style='padding: 0 0 15px 10px; text-align: left;'>
                <p style='font-size:1.4rem; font-weight:bold; color:var(--primary); margin:0;'>{APP_TITLE}</p>
                <p style='font-size: 0.7rem; color:var(--text-muted);'>{APP_SUBTITLE}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"👤 **{st.session_state.email}**")
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
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = label
                st.rerun()

        st.markdown("---")
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
