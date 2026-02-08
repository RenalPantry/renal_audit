import requests
import json
import streamlit as st

OCR_API_KEY = st.secrets.get("OCR_API_KEY")

@st.cache_data(show_spinner=False)
def perform_ocr(image_bytes):
    """
    Sends image bytes to OCR Space API and returns the detected text.
    """
    url = "https://api.ocr.space/parse/image"
    
    payload = {
        "apikey": OCR_API_KEY,
        "language": "eng",        # You can change to 'fre' for French
        "isOverlayRequired": False,
        "FileType": "JPG",
        "OCREngine": 2            # Engine 2 is better for tables/labels
    }
    
    # We pass the bytes directly as a file
    files = {
        "screenshot": ("image.jpg", image_bytes, "image/jpeg")
    }
    
    response = requests.post(url, data=payload, files=files, timeout=20)
    result = response.json()
    
    if result.get("OCRExitCode") == 1:
        # Success! Grab the full text
        return result["ParsedResults"][0]["ParsedText"]
    else:
        # Error handling (e.g., API key limit reached)
        error_msg = result.get("ErrorMessage", "Unknown Error")
        return f"Error: {error_msg}"