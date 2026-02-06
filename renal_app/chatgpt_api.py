import base64
import json
import streamlit as st
from openai import OpenAI

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")

def extract_label_info_from_image_real(image_file):
    """
    Extract nutritional label information from an image using OpenAI's vision API.

    Args:
        image_file: streamlit.UploadedFile or streamlit.CameraInput

    Returns:
        dict: Nutritional information in the format:
        {
            "Protein": "...",
            "Sodium": "...",
            "Potassium": "...",
            "Phosphorus": "...",
            "Sugar": "...",
            "Calories": "...",
            "Total Fat": "...",
            "Fiber": "..."
        }
        or {"error": "message"} if extraction fails.
    """
    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY not configured"}

    try:
        # Read the image and convert to base64
        image_data = image_file.read()
        base64_image = base64.standard_b64encode(image_data).decode("utf-8")

        # Determine media type from filename
        filename = image_file.name.lower()
        if filename.endswith('.png'):
            media_type = "image/png"
        elif filename.endswith(('.jpg', '.jpeg')):
            media_type = "image/jpeg"
        else:
            return {"error": "Unsupported image format"}

        # Call OpenAI API with vision
        client = OpenAI(api_key=OPENAI_API_KEY)
        message = client.chat.completions.create(
            model="gpt-4-vision",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": """
                            Extract the nutritional information and product identity from this label image. In English only. 
                            Return ONLY a JSON object with the following fields:
                            - "Product Name": The name of the product (e.g., "Greek Yogurt")
                            - "Serving Size": The numerical amount (e.g., "150" or "1")
                            - "Serving Unit": The unit of measure (e.g., "g", "ml", "cup", or "cookie")
                            - "Protein": Amount of protein (e.g., "10")
                            ... (keep your other nutrient fields) ...

                            If any field is missing, use null for that field.

                            Return ONLY the JSON:
                            {
                                "Product Name": "...",
                                "Brand": "...", 
                                "Serving Size": ...,
                                "Serving Unit": "...",
                                "Protein": ...,
                                "Sodium": ...,
                                "Potassium": ...,
                                "Phosphorus": ...,
                                "Sugar": ...,
                                "Calories": ...,
                                "Total Fat": ...,
                                "Fiber": ...,
                                "Ingredients": "..." 
                            """ 
                        }
                    ],
                }
            ],
            max_tokens=1024,
        )

        # Parse the response
        response_text = message.choices[0].message.content.strip()

        # Handle potential markdown code blocks
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        result = json.loads(response_text)
        return result

    except Exception as e:
        return {"error": f"Label extraction failed: {str(e)}"}

def extract_label_info_from_image(image_file):

    return {
        "Product Name": None,
        "Serving Size": 150,
        "Serving Unit": "g",
        "Protein": 10,
        "Sodium": 200,
        "Potassium": 300,
        "Phosphorus": 150,
        "Sugar": 5,
        "Calories": 150,
        "Total Fat": 8,
        "Fiber": 2
    }