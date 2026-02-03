import base64
import json
import streamlit as st
from openai import OpenAI

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")

def extract_product_info_from_image_real(image_file):
    """
    Extract product name and brand from an image using OpenAI's vision API.
    
    Args:
        image_file: streamlit.UploadedFile or streamlit.CameraInput
        
    Returns:
        dict: {"name": "...", "brand": "..."} or {"error": "message"} if extraction fails
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
                            "text": """Extract the product name and brand from this product image. 
Return ONLY a JSON object with two fields: "name" and "brand".
- "name": The product name/description (e.g., "Greek Yogurt", "Whole Milk")
- "brand": The brand name (e.g., "Chobani", "Organic Valley")

If you can't identify the information, use "Unknown" for that field.

Return ONLY the JSON, no other text:
{"name": "...", "brand": "..."}"""
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
        return {"error": f"Vision extraction failed: {str(e)}"}


def extract_product_info_from_image(image_file):
    """

    """
    return {"name": "Coconut Water", "brand": "Vita Coco"}