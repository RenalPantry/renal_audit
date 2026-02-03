import streamlit as st
from renal_app.styles import apply_custom_styles, nutrient_comparison_style
from renal_app.wizards import show_usda_wizard, show_label_wizard
from renal_app.logic import calculate_delta, get_audit_verdict
from renal_app.logic import units

# Page configuration
st.set_page_config(
    page_title="Renal Audit",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Apply custom styles
apply_custom_styles()

SAMPLE_DATA = {
    "Sugar": {"label": 12.5, "usda": 18.2},
    "Sodium": {"label": 140, "usda": 210},
    "Protein": {"label": 8.0, "usda": 7.5},
    "Fiber": {"label": 3.5, "usda": 3.2},
    "Calories": {"label": 200, "usda": 220},
    "Total Fat": {"label": 10, "usda": 12},
    "Potassium": {"label": 200, "usda": 220}
}

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

def audit_page():
    """Render the Audit page"""
    st.subheader("Audit", anchor=False)

    # The "Buttons" - This stays horizontal on mobile
    choice = st.segmented_control(
        label="Start Wizard", 
        options=["🔍 USDA Data*", "📸 Label Data"], 
        selection_mode="single",
        key="wizard_choice",
        width="stretch"
    )

    # Update the state based on selection
    if choice == "🔍 USDA Data*":
        st.session_state.wizard = "usda"
    elif choice == "📸 Label Data":
        st.session_state.wizard = "label"
    
    # Check which wizard was triggered
    wizard = st.session_state.get("wizard")
    if wizard == "usda":
        show_usda_wizard()
    elif wizard == "label":
        show_label_wizard()

    # Get audit verdict
    verdict, color = get_audit_verdict(SAMPLE_DATA)

    # Display verdict at the top with colored markdown
    if color == "red":
        st.markdown(
            f"""
            <div style="background-color: #ff4b4b; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="color: white; font-size: 1rem; font-weight: bold; margin: 0;">🚨 {verdict}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="background-color: #00cc66; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="color: white; font-size: 1rem; font-weight: bold; margin: 0;">✓ {verdict}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("")

    # Display comparison metrics
    st.subheader("Safety Flags", anchor=False)
    st.caption("Phosphorus & Gout Triggers to show if there is added phosphorus or ingredients that can cause gout.")

    # Display selected product info if available
    if 'selected_food_name' in st.session_state:
        product_name = st.session_state.get('selected_food_name', 'Unknown')
        st.info(f"**Product:** {product_name}")
    else:
        st.info("**Product:** Not Selected")

    st.divider()

    # Update the grid to include additional nutrients: Calories, Total Fat, and Fiber
    nutrients_to_display = ["Protein", "Sodium", "Potassium", "Sugar", "Calories", "Total Fat", "Fiber"]
    # Update column titles to match the table's background color
    st.markdown("""
<div style="display: grid; grid-template-columns: 1fr 100px 1fr; gap: 0.1rem; align-items: center; justify-content: center; margin-bottom: 0.5rem; padding: 0.25rem; min-height: 50px; background-color: {delta_color}; color: white; font-weight: bold;">
    <div style="text-align: center;">USDA</div>
    <div style="text-align: center;">Nutrient</div>
    <div style="text-align: center;">Label</div>
</div>
""", unsafe_allow_html=True)

    for nutrient in nutrients_to_display:
        values = SAMPLE_DATA.get(nutrient, {"label": 0, "usda": 0})
        delta_percent = calculate_delta(values['label'], values['usda'])
        delta_color = "#ff4b4b" if nutrient in ["Sugar", "Sodium", "Total Fat"] and delta_percent > 0 else "#00cc66"
        unit = units.get(nutrient, "")

        st.markdown(nutrient_comparison_style(values, delta_color, delta_percent, nutrient, unit), unsafe_allow_html=True)

    st.divider()

    # Add a section at the bottom for all ingredients
    st.subheader("All Ingredients", anchor=False)
    st.caption("For reference, this section lists all ingredients used in the product")

def matrix_page():
    """Render the Matrix page"""
    st.title("🔍 Matrix", anchor=False)
    st.info("Detailed audit data in tabular format - coming soon")
    
    # Placeholder for future matrix functionality
    st.markdown("""
    ### Planned Features:
    - Comprehensive data table with all audited products
    - Filter and search capabilities
    - Export to CSV functionality
    - Detailed discrepancy analysis
    """)

def pantry_page():
    """Render the Pantry page"""
    st.title("🥫 Pantry", anchor=False)
    st.info("Organize and track renal-friendly products - coming soon")
    
    # Placeholder for future pantry functionality
    st.markdown("""
    ### Planned Features:
    - Add and manage pantry items
    - Track expiration dates
    - Get product recommendations
    - View renal-friendly alternatives
    - Create shopping lists
    """)

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
    
    if st.sidebar.button("🔍 Matrix", key="nav_matrix", use_container_width=True, type="primary" if st.session_state.page == "Matrix" else "secondary"):
        st.session_state.page = "Matrix"
        st.rerun()
    
    if st.sidebar.button("🥫 Pantry", key="nav_pantry", use_container_width=True, type="primary" if st.session_state.page == "Pantry" else "secondary"):
        st.session_state.page = "Pantry"
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Compare label data against USDA lab truth for renal health")
    
    # Route to appropriate page
    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Audit":
        audit_page()
    elif st.session_state.page == "Matrix":
        matrix_page()
    elif st.session_state.page == "Pantry":
        pantry_page()

if __name__ == "__main__":
    main()
