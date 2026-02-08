"""Logic for calculations and audit verdicts."""

from copy import deepcopy

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
    "Protein": "g",
    "Sodium": "mg",
    "Potassium": "mg",
    "Phosphorus": "mg",
    "Sugar": "g",
    "Saturated Fat": "g",
    "Trans Fat": "g",
    "Calories": "kcal",
}

NUTRIENTS_TO_DISPLAY = [
    "Protein",
    "Sodium",
    "Potassium",
    "Phosphorus",
    "Sugar",
    "Saturated Fat",
    "Trans Fat",
    "Calories",
]

CRITICAL_NUTRIENTS = [
    "Protein",
    "Sodium",
    "Potassium",
    "Phosphorus",
    "Sugar",
    "Saturated Fat",
    "Trans Fat",
]

SAFETY_LIMITS = {
    "Protein": 15,
    "Sodium": 140,
    "Potassium": 200,
    "Phosphorus": 100,
    "Sugar": 15,
    "Saturated Fat": 5,
    "Trans Fat": 0.1,
}

COMPARISON_TEMPLATE = {
    "Protein": {"usda": None, "label": None},
    "Sodium": {"usda": None, "label": None},
    "Potassium": {"usda": None, "label": None},
    "Phosphorus": {"usda": None, "label": None},
    "Sugar": {"usda": None, "label": None},
    "Saturated Fat": {"usda": None, "label": None},
    "Trans Fat": {"usda": None, "label": None},
    "Calories": {"usda": None, "label": None},
}


def init_comparison_data():
    return deepcopy(COMPARISON_TEMPLATE)


def update_comparison_data(comparison_data, label_vals=None, usda_nutrients=None):
    if not comparison_data:
        comparison_data = init_comparison_data()

    for nutrient in comparison_data:
        if label_vals:
            comparison_data[nutrient]["label"] = label_vals.get(nutrient)
        if usda_nutrients:
            comparison_data[nutrient]["usda"] = usda_nutrients.get(nutrient)

    return comparison_data

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

def get_audit_details(data):
    report = {
        "status": "Renal Safe",
        "color": "green",
        "flags": [], # List of specific safety violations
        "discrepancies": [] # List of label vs usda mismatches
    }

    for nutrient in CRITICAL_NUTRIENTS:
        nutrient_info = data.get(nutrient, {"label": None, "usda": None})
        l_val = to_float(nutrient_info.get("label"))
        u_val = to_float(nutrient_info.get("usda"))
        limit = SAFETY_LIMITS.get(nutrient)

        # 1. Detail: Safety Limit Violation
        if limit and l_val > limit:
            excess = l_val - limit
            report["flags"].append(f"⚠️ Label {nutrient}: {l_val}{units.get(nutrient, '')} exceeds safe limit of {limit}{units.get(nutrient, '')} (+{excess}{units.get(nutrient, '')})")
            report["status"] = "High Renal Load"
            report["color"] = "red"

        if limit and u_val > limit:
            excess = u_val - limit
            report["flags"].append(f"⚠️ USDA {nutrient}: {u_val}{units.get(nutrient, '')} exceeds safe limit of {limit}{units.get(nutrient, '')} (+{excess}{units.get(nutrient, '')})")
            report["status"] = "High Renal Load"
            report["color"] = "red"

        # 2. Detail: USDA Discrepancy
        delta = calculate_delta(l_val, u_val)
        if delta and delta > 20:
            report["discrepancies"].append(f"🔍 {nutrient}: Label says {l_val}, but USDA suggests {u_val}")
            if report["color"] != "red": # Don't overwrite red with yellow
                report["status"] = "Data Mismatch"
                report["color"] = "yellow"

    return report
