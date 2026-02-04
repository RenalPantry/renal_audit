import requests
import streamlit as st
from rapidfuzz import fuzz

USDA_API_KEY = st.secrets.get("USDA_API_KEY")
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

def search_usda_foods(query, page_size=100):
    """
    Search the USDA FoodData Central database for foods matching the query.
    Args:
        query (str): The search term (food name, brand, etc.)
        page_size (int): Number of results to return (default 10)
    Returns:
        dict: JSON response from USDA API or error message
    """
    if not USDA_API_KEY:
        raise ValueError("USDA_API_KEY environment variable not set.")
    params = {
        "api_key": USDA_API_KEY,
        "query": query,
        "pageSize": page_size,
    }
    try:
        response = requests.get(USDA_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
    
def sort_results_by_relevance(foods, query):
    query = query.lower()
    for item in foods:
        description = item.get("description", "").lower()
        # Fallback to brandOwner if brandName is missing
        brand = (item.get("brandName") or item.get("brandOwner") or "").lower()
        
        # token_sort_ratio handles word order (e.g., "Yogurt Chobani" matches "Chobani Yogurt")
        desc_score = fuzz.token_sort_ratio(query, description)
        brand_score = fuzz.token_sort_ratio(query, brand) if brand else 0
        
        # Weighted average: Description is usually more unique than brand
        item["relevance_score"] = (desc_score * 0.5) + (brand_score * 0.5)
    
    # Sort descending (highest score first)
    return sorted(foods, key=lambda x: x["relevance_score"], reverse=True)

def clean_usda_label(text):
    if not text:
        return ""
    # 1. Take only the part before the first comma
    # clean_text = text.split(',')[0]
    clean_text = text.strip().title()
    # 2. Convert to Title Case (converts "GREEK YOGURT" to "Greek Yogurt")
    return clean_text

def display_and_select_usda_results(foods, search_query, radio_key="usda_product_radio"):
    """
    Display filtered USDA search results and handle user selection.
    Filters, sorts, and displays top 5 matches with radio selection.
    Stores selection in session state.
    
    Args:
        foods (list): List of food items from USDA API
        search_query (str): The original search query (used for relevance sorting)
        radio_key (str): Unique key for the radio button widget
        
    Returns:
        bool: True if a product was selected, False otherwise
    """
    if not foods:
        st.warning(f"No USDA matches found for '{search_query}'")
        return False
    
    # Step 1: Filter by allowed types
    allowed_types = ["Branded", "Foundation", "Survey (FNDDS)"]
    filtered_foods = [
        f for f in foods 
        if f.get("dataType") in allowed_types
    ]
    
    if not filtered_foods:
        st.warning("No matching foods in USDA database")
        return False
    
    # Step 2: Sort by relevance
    sorted_foods = sort_results_by_relevance(filtered_foods, search_query)
    top_matches = sorted_foods[:5]
    
    # Step 3: Build display options
    options = []
    captions = []
    id_map = {}
    caption_map = {}
    
    st.caption("Tap a product to select it")
    
    for item in top_matches:
        brand_name = (item.get('brandName') or item.get('brandOwner') or 'Generic').title()
        desc = clean_usda_label(item.get('description', ''))
        fdc_id = item.get('fdcId')
        weight = item.get('packageWeight')
        
        label = f"{brand_name}"
        caption = f"{desc}, {weight}"
        options.append(label)
        captions.append(caption)
        id_map[label] = fdc_id
        caption_map[label] = caption
    
    # Step 4: Radio selection widget
    selected_label = st.radio(
        "Select a product:",
        options=options,
        captions=captions,
        index=None,
        key=radio_key
    )
    
    # Step 5: Store selection in session state
    if selected_label:
        target_id = id_map[selected_label]
        selected_caption = caption_map[selected_label]
        st.session_state['selected_fdc_id'] = target_id
        st.session_state['selected_food_name'] = f"{selected_label} - {selected_caption}"
        st.success(f"✅ Selected USDA ID: {target_id}")
        return True
    
    return False

def usda_manual_entry_wizard():
    search_query = st.text_input("Enter product name (e.g., 'Greek Yogurt Liberte')", key="usda_search_input")

    if search_query:

        # 1. Fetch data from USDA
        results = search_usda_foods(search_query)

        if "error" in results:
            st.error(f"Error: {results['error']}")
        else:
            foods = results.get('foods', [])
            
            # 2. Display and handle selection
            display_and_select_usda_results(foods, search_query, radio_key="manual_entry_usda_radio")

def fetch_usda_food_details(fdc_id):
    results = search_usda_foods(fdc_id, page_size=1)
    foods = results.get('foods', [])
    
    if not foods:
        return {"error": "Food item not found."}
        
    food = foods[0]
    nutrients = {}

    # 1. Get the Serving Size (e.g., 30 for a 30g serving)
    # Most USDA Branded data is per 100g/ml
    serving_size = food.get("servingSize", 100) 
    # Calculate the ratio (e.g., 30/100 = 0.3)
    ratio = serving_size / 100

    # 2. Nutrient ID Map (Reliable IDs)
    id_map = {
        1003: "Protein",
        1093: "Sodium",
        1092: "Potassium",
        2000: "Sugar",
        1008: "Calories",
        1004: "Total Fat",
        1079: "Fiber"
    }

    for n in food.get("foodNutrients", []):
        n_id = n.get("nutrientId")
        if n_id in id_map:
            clean_name = id_map[n_id]
            raw_value = n.get("value", 0)
            
            # 3. SCALE THE VALUE
            # If USDA says 10g Protein per 100g, and serving is 30g, 
            # we save 3g (10 * 0.3)
            nutrients[clean_name] = round(raw_value * ratio, 2)

    return {
        "serving_size": serving_size,
        "serving_size_unit": food.get("servingSizeUnit", "g"),
        "nutrients": nutrients,
        "ingredients": food.get("ingredients", "N/A"),
        "brand_name": (food.get('brandName') or food.get('brandOwner') or 'Generic').title(),
        "product_description": clean_usda_label(food.get("description", "")),
        "FDC_ID": fdc_id
    }