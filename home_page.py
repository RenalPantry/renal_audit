import streamlit as st

def home_page():
    """Render the Home page with navigation buttons"""
    st.title("Renal Audit", anchor=False)

    st.markdown("""
    Choose a section to explore:
    """)

    st.markdown("")

    # Stack buttons vertically for mobile-friendly layout
    st.subheader("📊 Audit", anchor=False)
    st.markdown("""
    View nutritional analysis comparing label data against USDA laboratory truth.
    """)
    if st.button("Go to Audit →", key="audit_btn", use_container_width=True):
        st.session_state.page = "Audit"
        st.rerun()

    st.markdown("")

    if "NOT_USED" in st.session_state:

        st.subheader("🔍 Matrix", anchor=False)
        st.markdown(""" 
        Access detailed tabular audit records with filter and export capabilities.
        """)
        if st.button("Go to Matrix →", key="matrix_btn", use_container_width=True):
            st.session_state.page = "Matrix"
            st.rerun()

        st.markdown("")

        st.subheader("🥫 Pantry", anchor=False)
        st.markdown("""
        Manage pantry items and track renal-friendly products.
        """)
        if st.button("Go to Pantry →", key="pantry_btn", use_container_width=True):
            st.session_state.page = "Pantry"
            st.rerun()