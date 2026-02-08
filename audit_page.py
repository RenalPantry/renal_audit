import streamlit as st
from renal_app.airtable_api import prepare_airtable_record, push_to_airtable, push_to_airtable_with_attachment
from renal_app.gemini_api import analyze_ingredients_for_triggers
from renal_app.logic import (
    calculate_delta,
    units,
    get_audit_details,
    init_comparison_data,
    update_comparison_data,
    NUTRIENTS_TO_DISPLAY,
)
from renal_app.styles import nutrient_comparison_style
from renal_app.wizards import show_usda_wizard, show_label_wizard
from renal_app.usda_api import fetch_usda_food_details


def clear_session_keys(keys):
    for key in keys:
        st.session_state.pop(key, None)

def reset_label_data():
    clear_session_keys([
        "label_vals",
        "COMPARISON_DATA",
        "audit_report",
        "ai_report",
        "label_in",
    ])

    st.rerun()

def reset_usda_data():
    clear_session_keys([
        "food_details",
        "selected_fdc_id",
        "selected_food_name",
        "COMPARISON_DATA",
        "audit_report",
        "ai_report",
        "usda_in",
    ])

    st.rerun()

def audit_page():
    """Render the Audit page"""
    st.subheader("Audit", anchor=False)

    # The "Buttons" - This stays horizontal on mobile
    choice = st.segmented_control(
        "Start Wizard", 
        options=["🏷️ Label Data", "🔍 USDA Data"], 
        selection_mode="single",
        key="wizard_choice",
        width="stretch"
    )

    # Update the state based on selection
    if choice == "🔍 USDA Data":
        show_usda_wizard()
    elif choice == "🏷️ Label Data":
        show_label_wizard()

    st.session_state.setdefault("COMPARISON_DATA", init_comparison_data())
    st.session_state.setdefault("label_in", "Not Available")
    st.session_state.setdefault("usda_in", "Not Available")

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
        # 1. Always pull latest details if an ID exists
        label_vals = st.session_state.get("label_vals", {})
        fdc_id = st.session_state.get("selected_fdc_id")
        label_serving_size = label_vals.get("Serving Size") if label_vals else None
        food_details = fetch_usda_food_details(fdc_id, label_serving_size) if fdc_id else {}
        usda_nutrients = food_details.get("nutrients", {})

        # 2. Map both to the comparison table safely
        st.session_state["COMPARISON_DATA"] = update_comparison_data(
            st.session_state.get("COMPARISON_DATA"),
            label_vals=label_vals,
            usda_nutrients=usda_nutrients,
        )

        st.divider()

        # Display selected product info if available
        if "label_vals" in st.session_state:
            source = "Label"
            product = label_vals.get("Product Name")
            brand = label_vals.get("Brand")
            product_name = (f"{brand} {product}").strip() or "Unknown Product"
            if product_name == "Unknown Product" and "selected_food_name" in st.session_state:
                product_name = st.session_state["selected_food_name"]
            serving = label_vals.get('Serving Size')
            if serving is None:
                serving = "Serving size not provided, comparing with 100g USDA values"
                source = "USDA"
            s_unit = label_vals.get('Serving Unit')
            st.session_state["label_in"] = label_vals.get("Ingredients", "Not Available")

        else:
            source = "USDA"
            product = food_details.get("Product Name")
            brand = food_details.get("Brand")
            product_name = (f"{brand} {product}").strip() or "Unknown Product"
            serving = 100
            s_unit = food_details.get('Serving Unit')
            if s_unit is None:
                unit = "g"
            st.session_state["usda_in"] = food_details.get("Ingredients", "Not Available")

        st.markdown(f"**Product:** {product_name}")
        st.caption(f"**Serving Size:** {serving} {s_unit} | Source: {source}")

        # Update the grid to include additional nutrients: Calories, Total Fat, and Fiber
        nutrients_to_display = NUTRIENTS_TO_DISPLAY
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

        # Add a section at the bottom for all ingredients
        st.markdown("All Ingredients")
        if st.session_state.get("label_in") == "Not Available":
            st.caption(st.session_state["usda_in"])
        else:
            st.caption(st.session_state["label_in"])

        if st.button("▶️ Start Audit", use_container_width=True):
            with st.spinner("Sending data..."):

                st.session_state["audit_report"] = get_audit_details(st.session_state["COMPARISON_DATA"])
                st.session_state["ai_report"] = analyze_ingredients_for_triggers(st.session_state["label_in"], st.session_state["usda_in"])

                current_label = st.session_state.get("label_vals", {})
                current_usda = food_details # This is already fetched in your audit_page()
                current_photo = st.session_state.get("label_photo_bytes")
                final_payload = prepare_airtable_record(product, brand, serving, s_unit, current_usda, current_label, current_photo)
                push_to_airtable(final_payload)
                
                if not st.session_state["audit_report"]:
                    st.error("Failed to send data. Please try again.")
        
    if "audit_report" in st.session_state:
        # Display the audit banner
        with st.container(border=True):
            if "label_vals" in st.session_state:
                label_vals = st.session_state.get("label_vals", {})
                product_name = (f"{label_vals.get('Brand', '')} {label_vals.get('Product Name', '')}").strip() or "Unknown Product"
                if product_name == "Unknown Product":
                    product_name = st.session_state.get("selected_food_name", product_name)
            else:
                product_name = st.session_state.get("selected_food_name", "Unknown Product")

            if st.session_state["audit_report"]["color"] == "red" or st.session_state["ai_report"] != None:
                st.error(f"🔴 [ {product_name} ] High Renal Load")
                with st.expander("📊 Nutritional Numbers Audit"):
                    for flag in st.session_state["audit_report"]["flags"]:
                        st.write(flag)
                    if st.session_state["audit_report"]["discrepancies"]:
                        for disc in st.session_state["audit_report"]["discrepancies"]:
                            st.write(disc)
                with st.expander("🧪 AI Ingredient Analysis"):
                    st.write(st.session_state["ai_report"])
            
            elif st.session_state["audit_report"]["color"] == "yellow":
                st.warning(f"### 🟡 [ {product_name} ] Data Mismatch")
                with st.expander("📊 Nutritional Numbers Audit"):
                    for disc in st.session_state["audit_report"]["discrepancies"]:
                        st.write(disc)

            else:
                st.success(f"🟢 [ {product_name} ] Renal Safe")

            if st.button("Clear All Data", width='stretch'):
                reset_label_data()
                reset_usda_data()


