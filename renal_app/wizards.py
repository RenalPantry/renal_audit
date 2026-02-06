import io
import streamlit as st
from PIL import Image
from renal_app.usda_api import usda_manual_entry_wizard
from renal_app.chatgpt_api import extract_label_info_from_image
from renal_app.ocr_api import perform_ocr

def reset_wizard_choice():
    st.session_state.wizard_choice = None

def reset_wizard_label_step_navigator():
    st.session_state.label_step_navigator = None

def to_float(val):
    if val is None:
        return None
    return float(val)

def prepare_photo(img_file):
    img = Image.open(img_file)
    
    # 1. RESIZE: Shrink the long side to 1500px (Plenty for OCR)
    max_size = 1500
    ratio = max_size / max(img.size)
    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # 2. GRAYSCALE: High contrast helps the API see text
    img = img.convert("L")
    
    # 3. COMPRESS: Save as JPEG with 80% quality
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80, optimize=True)
    
    # This will almost always be 150KB - 400KB (Safe for 1MB limit!)
    return buf.getvalue()

def show_usda_wizard():
    """Wizard for USDA Data Input"""

    usda_manual_entry_wizard()

    if st.session_state.get('selected_fdc_id') and st.session_state.wizard_choice != None:
        st.button("📊 View Results", width="stretch", on_click=reset_wizard_choice)
    
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
                compressed_photo = prepare_photo(captured_photo)
                st.success("Photo captured! Processing...")
                st.markdown(perform_ocr(compressed_photo))  # Show raw OCR text for debugging
                st.session_state['label_vals'] = extract_label_info_from_image(compressed_photo)

        with tab2:
            uploaded_file = st.file_uploader("Choose an image", type=['jpg', 'jpeg', 'png'], key="label_upload")
            if uploaded_file:
                compressed_photo = prepare_photo(uploaded_file)
                st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
                st.markdown(perform_ocr(compressed_photo))  # Show raw OCR text for debugging
                st.session_state['label_vals'] = extract_label_info_from_image(compressed_photo)

    elif step == "Manual Entry":

        existing_data = st.session_state.get('label_vals', {})

        with st.form("label_form"):
            # We ensure 'value' is explicitly a float (e.g., 5.0 instead of 5)
            name_val = st.text_input("Product Name", value=existing_data.get("Product Name", ""))
            brand_val = st.text_input("Brand", value=existing_data.get("Brand", ""))
            sz_val = st.number_input("Serving Size", value=to_float(existing_data.get("Serving Size")), min_value=0.0, step=0.1)
            su_val = st.text_input("Serving Unit", value=existing_data.get("Serving Unit", ""))
            p_val = st.number_input("Protein (g)", value=to_float(existing_data.get("Protein")), min_value=0.0, step=0.1)
            s_val = st.number_input("Sodium (mg)", value=to_float(existing_data.get("Sodium")), min_value=0.0, step=1.0)
            k_val = st.number_input("Potassium (mg)", value=to_float(existing_data.get("Potassium")), min_value=0.0, step=1.0)
            phos_val = st.number_input("Phosphorus (mg)", value=to_float(existing_data.get("Phosphorus")), min_value=0.0, step=1.0)
            sug_val = st.number_input("Sugar (g)", value=to_float(existing_data.get("Sugar")), min_value=0.0, step=0.1)
            cal_val = st.number_input("Calories (kcal)", value=to_float(existing_data.get("Calories")), min_value=0.0, step=1.0)
            fat_val = st.number_input("Total Fat (g)", value=to_float(existing_data.get("Total Fat")), min_value=0.0, step=0.1)
            fib_val = st.number_input("Fiber (g)", value=to_float(existing_data.get("Fiber")), min_value=0.0, step=0.1)
            ingredients_val = st.text_area("Ingredients", value=existing_data.get("Ingredients", ""))
            
            submitted = st.form_submit_button("Save Label Data")
        
        if submitted:
            label_data = {
                "Product Name": name_val,
                "Brand": brand_val,
                "Serving Size": sz_val,
                "Serving Unit": su_val,
                "Protein": p_val,
                "Sodium": s_val,
                "Potassium": k_val,
                "Phosphorus": phos_val,
                "Sugar": sug_val,
                "Calories": cal_val,
                "Total Fat": fat_val,
                "Fiber": fib_val,
                "Ingredients": ingredients_val
            }
            
            st.session_state['label_vals'] = label_data
            st.success("Label data updated!")
            st.rerun()

    if st.session_state.get('label_vals') and st.session_state.label_step_navigator != None:
        st.button("📊 View Results", width="stretch", on_click=reset_wizard_label_step_navigator)
