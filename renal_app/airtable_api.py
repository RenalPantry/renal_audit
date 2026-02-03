import json
from datetime import datetime, timezone

import requests
import streamlit as st

AIRTABLE_API_KEY = st.secrets.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = st.secrets.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = st.secrets.get("AIRTABLE_TABLE_NAME")
AIRTABLE_TABLE_ID = st.secrets.get("AIRTABLE_TABLE_ID")

def prepare_airtable_record(usda_data):

    nutrient = usda_data.get("nutrients", {})

    # This dictionary keys MUST match your Airtable Column Names exactly
    record = {
        "Product": usda_data.get("product_description", ""),
        "Brand": usda_data.get("brand_name", ""),
        "FDC_ID": str(usda_data.get("FDC_ID", "")), # Best practice to keep the ID
        "Ingredients": usda_data.get("ingredients", ""),
        # Spread the nutrient data into the main dictionary
        "USDA Serving Size": usda_data.get("serving_size", ""),
        "USDA Serving Unit": usda_data.get("serving_size_unit", ""),
        "USDA Protein (g)": nutrient.get("Protein", 0),
        "USDA Sodium (mg)": nutrient.get("Sodium", 0),
        "USDA Potassium (mg)": nutrient.get("Potassium", 0),
        "USDA Sugar (g)": nutrient.get("Sugar", 0),
        "USDA Calories (kcal)": nutrient.get("Calories", 0),
        "USDA Total Fat (g)": nutrient.get("Total Fat", 0),
        "USDA Fiber (g)": nutrient.get("Fiber", 0),
    }
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

