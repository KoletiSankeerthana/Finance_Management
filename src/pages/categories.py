import streamlit as st
from src.database.crud import get_categories, add_category, delete_category

def render_categories():
    # --- Defensive Hardening (V12) ---
    if not st.session_state.get('authenticated'):
        st.warning("Please log in to access Category Management.")
        return
    if 'user_id' not in st.session_state:
        st.error("Session error: User ID missing. Please re-login.")
        return

    # V13 Hero Section
    st.markdown(f"""
    <div style="margin-bottom: 25px;">
        <h1 style="margin: 0; font-size: 2.5rem; background: linear-gradient(90deg, #00b4d8, #0077b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Category Mastery</h1>
        <p style="color: #a4b0be; font-size: 1.1rem; margin-top: 8px;">Organize your financial life with custom segments and visual markers.</p>
    </div>
    """, unsafe_allow_html=True)
    
    user_id = st.session_state.user_id
    
    # --- Form Auto-Reset Logic ---
    if 'cat_name' not in st.session_state: st.session_state.cat_name = ""
    if 'cat_emoji' not in st.session_state: st.session_state.cat_emoji = "🏷️"
    
    with st.expander("➕ Define New Segment", expanded=False):
        with st.form("add_cat_form_v13", clear_on_submit=False):
            col1, col2 = st.columns([2, 1])
            with col1:
                name = st.text_input("Segment Name", value=st.session_state.cat_name, key="v13_cat_name", placeholder="e.g., Luxury, Utilities...")
            with col2:
                emoji = st.text_input("Visual Marker (Icon/Emoji)", value=st.session_state.cat_emoji, key="v13_cat_icon")
                
            if st.form_submit_button("Create Category", use_container_width=True):
                if not name.strip():
                    st.error("Name is required.")
                else:
                    existing = [c['name'].lower() for c in get_categories(user_id)]
                    if name.lower().strip() in existing:
                        st.error(f"Category '{name}' already exists.")
                    elif add_category(user_id, name.strip(), emoji):
                        st.success(f"Category '{name}' created!")
                        st.session_state.cat_name = ""
                        st.session_state.cat_emoji = "🏷️"
                        st.rerun()
                    else:
                        st.error("Failed to create category.")

    st.markdown("---")
    
    # V14: Professional List Layout (Reverted from Grid)
    cats = get_categories(user_id)
    if cats:
        for cat in cats:
            with st.container():
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"""
                <div style='display: flex; align-items: center; padding: 15px; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border); margin-bottom: 0px;'>
                    <div style='font-size: 1.5rem; margin-right: 20px;'>{cat['emoji']}</div>
                    <div style='font-weight: 600; font-size: 1.1rem; color: #fafafa;'>{cat['name']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if c2.button("Delete", key=f"del_cat_v14_{cat['id']}", use_container_width=True):
                    success, message = delete_category(user_id, cat['name'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #a4b0be; border: 1px dashed var(--border); border-radius: 12px;">
            <p>Your workspace is empty. Create your first category above to begin tracking.</p>
        </div>
        """, unsafe_allow_html=True)
