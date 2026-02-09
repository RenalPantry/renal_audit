import json
import tempfile
import os
import io
from pyairtable import Api
import requests
import streamlit as st

AIRTABLE_API_KEY = st.secrets.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = st.secrets.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = st.secrets.get("AIRTABLE_TABLE_NAME")
AIRTABLE_TABLE_ID = st.secrets.get("AIRTABLE_TABLE_ID")

def prepare_airtable_record(product, brand, serving_size, unit, usda_data=None, label_data=None, image_bytes=None):
    # Ensure we are working with dictionaries even if None is passed
    usda = usda_data if usda_data else {}
    label = label_data if label_data else {}
    image = image_bytes if image_bytes else None

    # This dictionary will not crash because .get() returns None instead of erroring
    record = {
        "Product": product,
        "Brand": brand,        
        "Serving Size": serving_size,
        "Serving Unit": unit,
        "FDC_ID": str(st.session_state.get("selected_fdc_id",{})),

        "Label Protein (g)": label.get("Protein"),
        "Label Sodium (mg)": label.get("Sodium"),
        "Label Potassium (mg)": label.get("Potassium"),
        "Label Phosphorus (mg)": label.get("Phosphorus"),
        "Label Sugar (g)": label.get("Sugar"),
        "Label Saturated Fat (g)": label.get("Saturated Fat"),
        "Label Trans Fat (g)": label.get("Trans Fat"),
        "Label Calories (kcal)": label.get("Calories"),
        "Label Ingredients": label.get("Ingredients"),

        "USDA Protein (g)": usda.get("nutrients", {}).get("Protein"),
        "USDA Sodium (mg)": usda.get("nutrients", {}).get("Sodium"),
        "USDA Potassium (mg)": usda.get("nutrients", {}).get("Potassium"),
        "USDA Phosphorus (mg)": usda.get("nutrients", {}).get("Phosphorus"),
        "USDA Sugar (g)": usda.get("nutrients", {}).get("Sugar"),
        "USDA Saturated Fat (g)": usda.get("nutrients", {}).get("Saturated Fat"),
        "USDA Trans Fat (g)": usda.get("nutrients", {}).get("Trans Fat"),
        "USDA Calories (kcal)": usda.get("nutrients", {}).get("Calories"),
        "USDA Ingredients": usda.get("Ingredients"),
        
        # Meta Data
        "Audit Colour": st.session_state.get("audit_report", {}).get("color"),
        "Audit Result": f"{st.session_state.get('audit_report', {}).get('flags', '')}{st.session_state.get('audit_report', {}).get('discrepancies', '')}{st.session_state.get('ai_report', '')}",
    }
    
    return record

def push_to_airtable_with_attachment(payload_fields, image_bytes=None):
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)
    
    # 1. Create the record first (Text/Numbers only)
    record = table.create(payload_fields)
    
    # 2. Upload the attachment using a temporary file
    if image_bytes:
        # Create a temporary file that deletes itself after the 'with' block
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name  # This is the actual path on the disk
        
        try:
            # Pass the PATH string to Airtable
            table.upload_attachment(
                record["id"], 
                "Label Photo", 
                tmp_path
            )
        finally:
            # Clean up: remove the temp file from the server disk
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    return record

def push_to_airtable(record_dict):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Airtable expects a "fields" wrapper around the data
    payload = {"fields": record_dict}
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return True
    else:
        return False

