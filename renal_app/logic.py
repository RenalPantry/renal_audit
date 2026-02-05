# Logic for calculations and audit verdicts

# Nutritional units

units = {
    "Sugar": "g",
    "Sodium": "mg",
    "Protein": "g",
    "Fiber": "g",
    "Potassium": "mg",
    "Calories": "kcal",
    "Total Fat": "g",
    "Phosphorus": "mg"
}

def _coerce_number(value):
    if isinstance(value, (int, float)):
        return value
    return None

def calculate_delta(label_value, usda_value):
    """Calculate percentage difference between label and USDA values"""
    label = _coerce_number(label_value)
    usda = _coerce_number(usda_value)
    if label is None or usda is None or label == 0:
        return None
    return ((usda - label) / label) * 100

def get_audit_verdict(data):
    """Determine audit verdict based on data discrepancies"""
    critical_nutrients = ["Sugar", "Sodium", "Phosphorus"]
    for nutrient in critical_nutrients:
        nutrient_data = data.get(nutrient, {"label": None, "usda": None})
        delta = calculate_delta(nutrient_data.get("label"), nutrient_data.get("usda"))
        if delta is not None and delta > 10:  # More than 10% increase is an alert
            return "Alert", "red"
    return "Verified", "green"

