# Logic for calculations and audit verdicts

# Nutritional units

def to_float(val):
    """
    Safely converts any input (String, None, Int) to a Float.
    Returns 0.0 if the input is invalid or missing.
    """
    # 1. Handle None or empty values immediately
    if val is None or str(val).strip() == "" or str(val).lower() == "null":
        return 0.0
    
    try:
        # 2. Clean the string (remove commas or spaces just in case)
        if isinstance(val, str):
            val = val.replace(",", "").strip()
            
        # 3. Perform the conversion
        return float(val)
        
    except (ValueError, TypeError):
        # 4. If someone types "N/A" or "Unknown", return 0.0 instead of crashing
        return 0.0

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

def get_audit_details(data):
    # threshold configuration
    SAFETY_LIMITS = {"Sodium": 200, "Potassium": 200, "Sugar": 15}
    
    report = {
        "status": "Verified",
        "color": "green",
        "flags": [], # List of specific safety violations
        "discrepancies": [] # List of label vs usda mismatches
    }

    critical_nutrients = ["Sodium", "Potassium", "Phosphorus", "Sugar"]

    for nutrient in critical_nutrients:
        nutrient_info = data.get(nutrient, {"label": None, "usda": None})
        l_val = to_float(nutrient_info.get("label"))
        u_val = to_float(nutrient_info.get("usda"))
        limit = SAFETY_LIMITS.get(nutrient)

        # 1. Detail: Safety Limit Violation
        if limit and l_val > limit:
            excess = l_val - limit
            report["flags"].append(f"⚠️ {nutrient}: {l_val}mg exceeds safe limit of {limit}mg (+{excess}mg)")
            report["status"] = "High Risk"
            report["color"] = "red"

        # 2. Detail: USDA Discrepancy
        delta = calculate_delta(l_val, u_val)
        if delta and delta > 15:
            report["discrepancies"].append(f"🔍 {nutrient}: Label says {l_val}, but USDA suggests {u_val}")
            if report["color"] != "red": # Don't overwrite red with yellow
                report["status"] = "Accuracy Warning"
                report["color"] = "yellow"

    return report
