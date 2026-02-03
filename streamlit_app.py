import streamlit as st
from renal_app.styles import apply_custom_styles
from home_page import home_page
from audit_page import audit_page

def main():
    """Main application logic"""

    # Initialize session state for page navigation if not exists
    if 'page' not in st.session_state:
        st.session_state.page = "Home"

    # Sidebar navigation
    st.sidebar.title("Renal Audit")
    st.sidebar.markdown("")

    # Create navigation buttons with icons
    if st.sidebar.button("🏠 Home", key="nav_home", use_container_width=True, type="primary" if st.session_state.page == "Home" else "secondary"):
        st.session_state.page = "Home"
        st.rerun()

    if st.sidebar.button("📊 Audit", key="nav_audit", use_container_width=True, type="primary" if st.session_state.page == "Audit" else "secondary"):
        st.session_state.page = "Audit"
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption("Compare label data against USDA lab truth for renal health")

    # Route to appropriate page
    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Audit":
        audit_page()

if __name__ == "__main__":
    # Page configuration
    st.set_page_config(
        page_title="Renal Audit",
        page_icon="🏥",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # Apply custom styles
    apply_custom_styles()

    main()
