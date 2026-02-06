import streamlit as st
from renal_app.airtable_api import prepare_airtable_record, push_to_airtable
from renal_app.logic import calculate_delta, units, get_audit_details
from renal_app.styles import nutrient_comparison_style
from renal_app.wizards import show_usda_wizard, show_label_wizard
from renal_app.usda_api import fetch_usda_food_details

def reset_label_data():
    if "label_vals" in st.session_state:
        del st.session_state["label_vals"] # Key is GONE. 'if' will now be False.
    if "COMPARISON_DATA" in st.session_state:
        del st.session_state["COMPARISON_DATA"] # Clear the entire comparison data to reset both label and usda values
    
    st.rerun()  

def reset_usda_data():
    if "usda_vals" in st.session_state:
        del st.session_state["usda_vals"] # Key is GONE. 'if' will now be False.
    if "selected_fdc_id" in st.session_state:
        del st.session_state["selected_fdc_id"]
    if "selected_food_name" in st.session_state:
        del st.session_state["selected_food_name"]
    if "COMPARISON_DATA" in st.session_state:
        del st.session_state["COMPARISON_DATA"] # Clear the entire comparison data to reset both label and usda values

    st.rerun()

def audit_page():
    """Render the Audit page"""
    st.subheader("Audit", anchor=False)

    # The "Buttons" - This stays horizontal on mobile
    choice = st.segmented_control(
        "Start Wizard", 
        options=["📸 Label Data*", "🔍 USDA Data"], 
        selection_mode="single",
        key="wizard_choice",
        width="stretch"
    )

    # Update the state based on selection
    if choice == "🔍 USDA Data":
        show_usda_wizard()
    elif choice == "📸 Label Data*":
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

    if ("label_vals" not in st.session_state) and ("selected_fdc_id" not in st.session_state):
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

        if "label_vals" in st.session_state:
            label_vals = st.session_state.get("label_vals", {})
            for n in st.session_state["COMPARISON_DATA"]:
            # We reach inside the dictionary to change just the 'usda' part
                st.session_state["COMPARISON_DATA"][n]["label"] = label_vals.get(n)

        if "usda_info" in st.session_state:
            usda_vals = food_details.get("nutrients", {})
            for n in st.session_state["COMPARISON_DATA"]:
                # We reach inside the dictionary to change just the 'usda' part
                st.session_state["COMPARISON_DATA"][n]["usda"] = usda_vals.get(n)

        st.divider()

        audit_report = get_audit_details(st.session_state["COMPARISON_DATA"])

        # Display the main banner
        st.subheader(f"Audit Status: {audit_report['status']}")

        if audit_report["color"] == "red":
            st.error("RED LIGHT", icon ="🚫")
            for flag in audit_report["flags"]:
                st.write(flag)
            
            if audit_report["discrepancies"]:
                st.warning("Note: Significant differences found between Label and USDA data.")
                for disc in audit_report["discrepancies"]:
                    st.write(disc)

        elif audit_report["color"] == "yellow":
            st.warning("⚠️ ###Accuracy Warning")
            for disc in audit_report["discrepancies"]:
                st.write(disc)

        else:
            st.success("✅ This item appears safe based on your current limits.")

        # Display selected product info if available
        if "label_vals" in st.session_state:
            source = "Label"
            product_name = (f"{label_vals.get('Brand', '')} {label_vals.get('Product Name', '')}").strip() or "Unknown Product"
            serving = label_vals.get('Serving Size')
            if serving is None:
                serving = "Serving size not provided, comparing with 100g USDA values"
                source = "USDA"
            unit = label_vals.get('Serving Unit')           
        else:
            source = "USDA"
            product_name = st.session_state.get('selected_food_name', 'Unknown')
            serving = 100
            unit = usda_vals.get('Serving Unit')
            if unit is None:
                unit = "g"

        st.subheader(f"**Product:** {product_name}")
        st.info(f"**Serving Size:** {serving} {unit}")
        st.caption(f"Source: {source}")

        # Update the grid to include additional nutrients: Calories, Total Fat, and Fiber
        nutrients_to_display = ["Protein", "Sodium", "Potassium", "Phosphorus", "Sugar", "Calories", "Total Fat", "Fiber"]
        # Update column titles to match the table's background color
        st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 100px 1fr; gap: 0.1rem; align-items: center; justify-content: center; margin-bottom: 0.5rem; padding: 0.25rem; min-height: 50px; background-color: #0e1117; color: white; font-weight: bold; border-bottom: 2px solid #31333F;">
        <div style="text-align: center;">Label</div>
        <div style="text-align: center;">Nutrient</div>
        <div style="text-align: center;">USDA</div>
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

        st.markdown("")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Clear Label Data", use_container_width=True):
                reset_label_data()

        with col2:
            if st.button("Clear USDA Data", use_container_width=True):
                reset_usda_data()

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