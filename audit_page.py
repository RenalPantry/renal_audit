import streamlit as st
from renal_app.airtable_api import prepare_airtable_record, push_to_airtable
from renal_app.logic import calculate_delta, get_audit_verdict, units
from renal_app.styles import nutrient_comparison_style
from renal_app.wizards import show_usda_wizard, show_label_wizard
from renal_app.usda_api import fetch_usda_food_details

def audit_page():
    """Render the Audit page"""
    st.subheader("Audit", anchor=False)

    # The "Buttons" - This stays horizontal on mobile
    choice = st.segmented_control(
        label="Start Wizard", 
        options=["📸 Label Data*", "🔍 USDA Data"], 
        selection_mode="single",
        key="wizard_choice",
        width="stretch"
    )

    # Update the state based on selection
    if choice == "🔍 USDA Data":
        st.session_state.wizard = "usda"
    elif choice == "📸 Label Data*":
        st.session_state.wizard = "label"

    # Check which wizard was triggered
    wizard = st.session_state.get("wizard")
    if wizard == "usda":
        show_usda_wizard()
    elif wizard == "label":
        show_label_wizard()

    # Initialize the structure ONLY if it doesn't exist
    if "COMPARISON_DATA" not in st.session_state:
        st.session_state["COMPARISON_DATA"] = {
            "Protein": {"usda": None, "label": None},
            "Sodium": {"usda": None, "label": None},
            "Potassium": {"usda": None, "label": None},
            "Phosphorus": {"usda": None, "label": None},
            "Sugar": {"usda": None, "label": None},
            "Calories": {"usda": None, "label": None},
            "Total Fat": {"usda": None, "label": None},
            "Fiber": {"usda": None, "label": None},
        }

    food_details = st.session_state.get("current_food_details", None)

    if "label_info" in st.session_state:
        label_vals = st.session_state.get("label_info", {})
        for n in st.session_state["COMPARISON_DATA"]:
        # We reach inside the dictionary to change just the 'usda' part
            st.session_state["COMPARISON_DATA"][n]["label"] = label_vals.get(n)

    if "label_info" not in st.session_state:
            st.markdown(
            f"""
            <div style="background-color: #2C7A7B; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="color: white; font-size: 1rem; font-weight: bold; margin: 0;">Please select a product to audit.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Fetch detailed food data if not already fetched
        food_details = fetch_usda_food_details(st.session_state.get("selected_fdc_id"))

        # Update USDA values (Do NOT use = { ... })
        usda_vals = food_details.get("nutrients", {})
        for n in st.session_state["COMPARISON_DATA"]:
            # We reach inside the dictionary to change just the 'usda' part
            st.session_state["COMPARISON_DATA"][n]["usda"] = usda_vals.get(n)

        # Get audit verdict
        verdict, color = get_audit_verdict(st.session_state.get("COMPARISON_DATA", {}))

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

    if food_details:
        # Display comparison metrics
        st.subheader("Safety Flags", anchor=False)
        st.caption("Phosphorus & Gout Triggers to show if there is added phosphorus or ingredients that can cause gout.")

        # Display selected product info if available
        product_name = st.session_state.get('selected_food_name', 'Unknown')
        st.info(f"**Product:** {product_name}")

        serving = food_details.get('serving_size', 'N/A')
        unit = food_details.get('serving_size_unit', '')
        st.markdown(f"**Serving Size:** {serving} {unit}")

        st.divider()

        # Update the grid to include additional nutrients: Calories, Total Fat, and Fiber
        nutrients_to_display = ["Protein", "Sodium", "Potassium", "Phosphorus", "Sugar", "Calories", "Total Fat", "Fiber"]
        # Update column titles to match the table's background color
        st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 100px 1fr; gap: 0.1rem; align-items: center; justify-content: center; margin-bottom: 0.5rem; padding: 0.25rem; min-height: 50px; background-color: #0e1117; color: white; font-weight: bold;">
        <div style="text-align: center;">USDA</div>
        <div style="text-align: center;">Nutrient</div>
        <div style="text-align: center;">Label</div>
        </div>
        """, unsafe_allow_html=True)
        # Map nutrients to COMPARISON_DATA

        for nutrient in nutrients_to_display:
            # Ensure values have the required structure
            values = st.session_state.get("COMPARISON_DATA", {}).get(nutrient, {"label": None, "usda": None})
            label_value = values.get("label")
            usda_value = values.get("usda")

            delta_percent = calculate_delta(label_value, usda_value)
            if delta_percent is None:
                delta_color = "#666"
            else:
                delta_color = "#ff4b4b" if delta_percent > 0 else "#00cc66"
            unit = units.get(nutrient, "")

            # Pass validated values to nutrient_comparison_style
            st.markdown(nutrient_comparison_style({"label": label_value, "usda": usda_value}, delta_color, delta_percent, nutrient, unit), unsafe_allow_html=True)

        st.divider()

        # Add a section at the bottom for all ingredients
        st.subheader("All Ingredients", anchor=False)
        ingredients = food_details.get("ingredients", "Not Available")
        st.caption(ingredients)

        # Display a preview of exactly what is going to Airtable
        final_payload = prepare_airtable_record(food_details)
        
        if st.button("🚀 Send to Audit Database"):
            with st.spinner("Sending data..."):
                success = push_to_airtable(final_payload)
                
                if success:
                    st.success("Successfully added to Audit Database!")
                    st.balloons()
                else:
                    st.error("Failed to send data. Please try again.")