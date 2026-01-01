import streamlit as st
import time
from src.database.crud import add_category, get_categories, delete_category, load_transactions_df

def render_categories():
    if not st.session_state.get('authenticated'):
        st.warning("Please log in.")
        return

    user_id = st.session_state.user_id

    st.markdown(f"""
    <div style="margin-bottom: 20px; text-align: center;">
        <h1 class='app-header-title'>CATEGORIES</h1>
        <p class='app-header-subtitle'>Custom Categories</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Add Category ---
    with st.expander("➕ Add New Category", expanded=True):
        with st.form("add_cat_form", clear_on_submit=True):
            c1, c2 = st.columns([3, 1])
            name = c1.text_input("Category Name")
            emoji = c2.text_input("Icon (e.g. 🍔)", value="🏷️")
            
            if st.form_submit_button("Add Category", type="primary"):
                if not name:
                    st.error("Name is required.")
                else:
                    if add_category(user_id, name, emoji):
                        st.success(f"Category '{name}' added!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Error adding category.")

    st.markdown("### Your Categories")
    
    cats = get_categories(user_id)
    # Load transactions strictly for real-time counting
    from src.database.crud import load_transactions_df
    expenses_df = load_transactions_df(user_id)
    
    # REQUIRED DATA LOGIC: Calculate strictly from expenses
    if not expenses_df.empty:
        from src.utils.navigation import clean_category_icons
        expenses_df = clean_category_icons(expenses_df.copy(), user_id=user_id)
        # Pandas-style logic as requested:
        txn_counts = (
            expenses_df
            .groupby("category")
            .size()
            .to_dict()
        )
    else:
        txn_counts = {}
    
    if cats:
        for cat in cats:
            # Transaction count must be calculated ONLY from expenses
            category_name = cat['name']
            count = txn_counts.get(category_name, 0)
            
            # UI Layout (Keep Same)
            c1, c2, c3 = st.columns([0.4, 3.6, 1.2]) 
            with c1:
                st.markdown(f"<h4 style='margin:0; font-size:1.4rem;'>{cat['emoji']}</h4>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<p style='margin:0; font-size:0.95rem; font-weight:600;'>{category_name}</p>", unsafe_allow_html=True)
                st.caption(f"{count} transactions linked")
            
            with c3:
                # DELETE OPTION RULE
                if count > 0:
                    # Disable delete checkbox and show info text (Mandatory)
                    st.info("Cannot delete – expenses exist")
                else:
                    # Allow delete checkbox if count == 0
                    confirm = st.checkbox("Delete", key=f"conf_{cat['id']}")
                    if confirm:
                        if st.button(f"Confirm 🗑️", key=f"del_{cat['id']}", type="primary"):
                            success, msg = delete_category(user_id, category_name)
                            if success:
                                st.success(msg)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(msg)
            
            st.markdown("<div style='margin: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1);'></div>", unsafe_allow_html=True)
    else:
        st.info("No categories found.")

    from src.utils.navigation import render_bottom_nav
    render_bottom_nav("categories")
