import streamlit as st

def home_page():
    """Render the Home page with navigation buttons"""
    st.title("Renal Audit System", anchor=False)

    st.markdown("")

    # Stack buttons vertically for mobile-friendly layout
    st.subheader("📊 Audit", anchor=False)
    st.markdown("""
    View nutritional analysis comparing label data against USDA laboratory truth.
    """)
    if st.button("🚀 Start New Audit →", key="audit_btn", use_container_width=True):
        st.session_state.page = "Audit"
        st.rerun()

    st.markdown("")

    st.write("### **How to Perform an Audit**")

    st.markdown("""
    **1. Capture & Extract:**
    Upload a photo of the nutrition label. The system will automatically extract Sodium, Potassium, and Phosphorus.
    
    **2. Cross-Reference:**
    Search the USDA database to find the official matching item to compare "Label vs. Reality."

    **3. Review & Edit:**
    Check the AI results. You can manually adjust any numbers in the table before finalizing.
    
    **4. Sync to Database:**
    Click **'Start Audit'** to calculate the variance and log the results to the central registry.
    """)

    st.markdown("")

    st.markdown("""
    **💡 Tips for Best Results**
    * **Photo Quality:** Use high-resolution images with the text facing upright.
    * **Units:** Double-check if the serving size on the label matches the USDA entry.
    """)

    st.markdown("")

# --- CONTACT & FEEDBACK ---
    st.write("### **Support & Feedback**")
    
    c1, c2 = st.columns(2)
    
    with c1:
        # Mailto link: This opens the user's default email app
        st.markdown(f"""
        **Found a bug?** Please email us at:""")
        st.link_button("📩 Email Feedback", f"mailto:hello@renalpantry.com?subject=Renal%20Audit%20Feedback")

    with c2:
        # Website Link
        st.markdown("**Learn more about us:**")
        st.link_button("🌐 Visit Our Website", "https://renalpantry.com/")

    st.divider()

    st.caption("⚠️ **Disclaimer:** This tool is intended for data verification purposes only. AI-generated extractions should be manually reviewed for accuracy before submission. Not a substitute for professional medical or dietetic advice.")

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