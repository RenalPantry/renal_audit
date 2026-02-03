import streamlit as st
from renal_app.wizards import show_usda_wizard, show_label_wizard
from renal_app.logic import calculate_delta, get_audit_verdict
from renal_app.logic import units
from renal_app.styles import nutrient_comparison_style

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

    if "selected_food_name" not in st.session_state:
            st.markdown(
            f"""
            <div style="background-color: #2C7A7B; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="color: white; font-size: 1rem; font-weight: bold; margin: 0;">Please select a product to audit.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Get audit verdict
        verdict, color = get_audit_verdict(st.session_state.get("SAMPLE_DATA", {}))

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

    st.markdown("Serving Size: ")

    st.divider()

    # Update the grid to include additional nutrients: Calories, Total Fat, and Fiber
    nutrients_to_display = ["Protein", "Sodium", "Potassium", "Sugar", "Calories", "Total Fat", "Fiber"]
    # Update column titles to match the table's background color
    st.markdown("""
<div style="display: grid; grid-template-columns: 1fr 100px 1fr; gap: 0.1rem; align-items: center; justify-content: center; margin-bottom: 0.5rem; padding: 0.25rem; min-height: 50px; background-color: #0e1117}; color: white; font-weight: bold;">
    <div style="text-align: center;">USDA</div>
    <div style="text-align: center;">Nutrient</div>
    <div style="text-align: center;">Label</div>
</div>
""", unsafe_allow_html=True)

    for nutrient in nutrients_to_display:
        # Ensure values have the required structure
        values = st.session_state.get("SAMPLE_DATA", {}).get(nutrient, {"label": 0, "usda": 0})
        label_value = values.get("label", 0)
        usda_value = values.get("usda", 0)

        delta_percent = calculate_delta(label_value, usda_value)
        delta_color = "#ff4b4b" if nutrient in ["Sugar", "Sodium", "Total Fat"] and delta_percent > 0 else "#00cc66"
        unit = units.get(nutrient, "")

        # Pass validated values to nutrient_comparison_style
        st.markdown(nutrient_comparison_style({"label": label_value, "usda": usda_value}, delta_color, delta_percent, nutrient, unit), unsafe_allow_html=True)

    st.divider()

    # Add a section at the bottom for all ingredients
    st.subheader("All Ingredients", anchor=False)
    st.caption("For reference, this section lists all ingredients used in the product")