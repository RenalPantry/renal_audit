import streamlit as st
from renal_app.usda_api import (
    usda_manual_entry_wizard, 
    search_usda_foods, 
    display_and_select_usda_results
)
from renal_app.chatgpt_api import extract_product_info_from_image

def reset_wizard_usda_step_navigator():
    st.session_state.usda_step_navigator = None

def show_usda_wizard():
    """Wizard for USDA Data Input"""

    step = st.segmented_control(
        "USDA Data Search By",
        options=["Auto Detect", "Manual Entry"],
        selection_mode="single",
        key="usda_step_navigator",
        width="stretch"
    )

    if step == "Auto Detect":
        tab1, tab2 = st.tabs(["📸 Take Photo", "📁 Upload Image"])
        
        with tab1:
            captured_photo = st.camera_input("Scan Product", key="usda_camera")
            if captured_photo:
                st.success("Photo captured! Processing...")
                process_product_image(captured_photo)

        with tab2:
            uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'jpeg', 'png'], key="usda_upload")
            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
                process_product_image(uploaded_file)

    elif step == "Manual Entry":
        usda_manual_entry_wizard()

    if st.session_state.get('selected_fdc_id') and st.session_state.usda_step_navigator != None:
        st.button("📊 View Results", width="stretch", on_click=reset_wizard_usda_step_navigator)


def process_product_image(image_file):
    """
    Process a product image to extract name/brand and search USDA database.
    """
    with st.spinner("🔍 Analyzing image..."):
        # Step 1: Extract product info from image using ChatGPT
        extracted_info = extract_product_info_from_image(image_file)
        
        if "error" in extracted_info:
            st.error(f"❌ {extracted_info['error']}")
            return
        
        # Step 2: Build search query from extracted info
        product_name = extracted_info.get("name", "Unknown")
        brand = extracted_info.get("brand", "Unknown")
        search_query = f"{brand} {product_name}".strip()
        
        st.info(f"📦 Detected: **{brand}** - *{product_name}*")
    
    # Step 3: Search USDA foods
    with st.spinner("Searching USDA database..."):
        results = search_usda_foods(search_query)
    
    if "error" in results:
        st.error(f"USDA Search Error: {results['error']}")
        return
    
    foods = results.get('foods', [])
    
    # Step 4: Display results and handle selection (shared function)
    display_and_select_usda_results(foods, search_query, radio_key="auto_detect_usda_radio")

def show_label_wizard():
    """Wizard for Label Data Input"""

    step = st.segmented_control(
        "Label Data Entry Method",
        options=["Auto Detect", "Manual Entry"],
        selection_mode="single",
        key="label_step_navigator",
        width="stretch"
    )
    
    if step == "Auto Detect":
        tab1, tab2 = st.tabs(["📸 Take Photo", "📁 Upload Image"])
        
        with tab1:
            captured_photo = st.camera_input("Scan Nutrition Label", key="label_camera")
            if captured_photo:
                st.success("Photo captured! Processing...")
                # TODO: Implement nutrition label OCR extraction

        with tab2:
            uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'jpeg', 'png'], key="label_upload")
            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
                # TODO: Implement nutrition label OCR extraction

    elif step == "Manual Entry":
        with st.form("label_form"):
            st.number_input("Protein (g)", min_value=0.0, step=0.1)
            st.number_input("Sodium (mg)", min_value=0.0, step=1.0)
            st.number_input("Potassium (mg)", min_value=0.0, step=1.0)
            st.number_input("Sugar (g)", min_value=0.0, step=0.1)
            submitted = st.form_submit_button("Submit")
            if submitted:
                st.success("Label data submitted successfully!")