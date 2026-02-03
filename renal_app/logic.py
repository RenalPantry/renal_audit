# Logic for calculations and audit verdicts

# Nutritional units

units = {
    "Sugar": "g",
    "Sodium": "mg",
    "Protein": "g",
    "Fiber": "g",
    "Potassium": "mg",
    "Calories": "kcal",
    "Total Fat": "g"
}

def calculate_delta(label_value, usda_value):
    """Calculate percentage difference between label and USDA values"""
    if label_value == 0:
        return 0
    return ((usda_value - label_value) / label_value) * 100

def get_audit_verdict(data):
    """Determine audit verdict based on data discrepancies"""
    critical_nutrients = ["Sugar", "Sodium"]
    for nutrient in critical_nutrients:
        delta = calculate_delta(data[nutrient]["label"], data[nutrient]["usda"])
        if delta > 10:  # More than 10% increase is an alert
            return "Alert", "red"
    return "Verified", "green"

