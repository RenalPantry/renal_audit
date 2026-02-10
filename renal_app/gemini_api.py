import google.generativeai as genai
import streamlit as st
import os
import json
import re

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

# Configure your API Key (Best practice: use st.secrets or env vars)
genai.configure(api_key=GEMINI_API_KEY)


@st.cache_resource
def get_gemini_model():
    return genai.GenerativeModel("gemini-2.5-flash-lite")

@st.cache_data(show_spinner=False)
def extract_label_info_from_ocr(ocr_text):
    """
    Converts messy OCR text into a structured dictionary for st.session_state['label_vals'].
    """
    if not ocr_text:
        return {}

    model = get_gemini_model()

    prompt = f"""
    You are a data extraction expert. I will provide messy OCR text from a nutrition label.
    Extract the following fields into a valid JSON object. 
    
    RULES:
    1. Use ONLY these keys: "Product Name", "Brand", "Serving Size", "Serving Unit", "Protein", "Sodium", "Potassium", "Phosphorus", "Sugar", "Calories", "Saturated Fat", "Trans Fat", "Ingredients".
    2. Convert all nutrient values to numbers (floats). Do not include units like 'mg' or 'g' in the values.
    3. If a value is missing, use null.
    4. For 'Ingredients', extract the full comma-separated list.
    5. Clean up OCR typos (e.g., 'S0dium' -> 'Sodium').
    6. Get serving size in g or mL if possible.
    7. Capitalize the first letter only for Product Name and Brand.

    OCR TEXT:
    {ocr_text}

    RETURN ONLY THE JSON OBJECT.
    """

    try:
        response = model.generate_content(prompt)
        # Clean the response text to ensure it's valid JSON
        clean_json = re.search(r'\{.*\}', response.text, re.DOTALL).group()
        data = json.loads(clean_json)
        return data
    except Exception as e:
        st.error(f"AI Extraction Error: {e}")
        return {}

@st.cache_data(show_spinner=False)
def analyze_ingredients_for_triggers(label_in_text, usda_in_text):
    """
    Analyzes raw ingredient text for CKD/Gout triggers that numbers miss.
    Returns a list of strings (warnings).
    """
    if not label_in_text or label_in_text == "Not Available":
        if not usda_in_text or usda_in_text == "Not Available":
            return None

    model = get_gemini_model()

    prompt = f"""
    You are a clinical renal dietitian and gout specialist. 
    Analyze the following ingredient list for specific 'Hidden Triggers':
    
    1. PHOSPHORUS ADDITIVES: Look for 'phos' (e.g., Sodium Tripolyphosphate, Phosphoric Acid).
    2. GOUT TRIGGERS: High-purine items (Yeast Extract, Organ Meats, Anchovies) and High Fructose Corn Syrup.
    3. POTASSIUM SALTS: (e.g., Potassium Chloride) used as salt substitutes.
    4. INFLAMMATORY FATS: (Trans-fats, Hydrogenated oils, Lard).

    INGREDIENTS:
    {label_in_text}{usda_in_text}

    OUTPUT FORMAT:
    Return ONLY a JSON list of strings. Each string should be a short warning.
    Example: ["Contains Phosphoric Acid (Hidden Phosphorus)", "Contains High Fructose Corn Syrup (Gout Trigger)"]
    If no triggers are found, return None.
    """

    try:
        response = model.generate_content(prompt)
        
        # Extract JSON from the response text (cleaning up any markdown code blocks)
        text = response.text
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        
        if json_match:
            return json.loads(json_match.group())
        return None

    except Exception as e:
        st.error(f"Error calling Gemini API: {e}")
        return ["Error analyzing ingredients."]
    