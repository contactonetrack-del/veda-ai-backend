"""
Premium Estimator Tool
Estimates health insurance premium based on age, coverage, and family size
Based on typical Indian health insurance market rates (2024-2025)
"""
from typing import Dict


def estimate_premium(
    age: int,
    sum_insured_lakhs: float,
    family_type: str = "individual"
) -> Dict:
    """
    Estimate health insurance premium
    
    Args:
        age: Age of the primary insured (or eldest member for family)
        sum_insured_lakhs: Coverage amount in lakhs (e.g., 5, 10, 15, 25)
        family_type: "individual", "couple", "family" (2A+2C), "parents"
    
    Returns:
        Dict with estimated premium range and breakdown
    """
    if age < 18:
        return {
            "success": False,
            "message": "Primary insured must be at least 18 years old"
        }
    
    if age > 65:
        return {
            "success": False,
            "message": "For seniors above 65, please consult directly with insurers for accurate quotes"
        }
    
    if sum_insured_lakhs < 1:
        return {
            "success": False,
            "message": "Minimum sum insured should be 1 Lakh"
        }
    
    # Base premium rates per lakh (approximate for 30-year-old individual)
    # These are simplified averages - actual premiums vary by insurer
    base_rate_per_lakh = 500  # Rs per lakh for young adult
    
    # Age factor (premium increases with age)
    if age <= 25:
        age_factor = 0.8
    elif age <= 35:
        age_factor = 1.0
    elif age <= 45:
        age_factor = 1.5
    elif age <= 55:
        age_factor = 2.2
    else:  # 56-65
        age_factor = 3.0
    
    # Family type factor
    family_factors = {
        "individual": 1.0,
        "couple": 1.8,
        "family": 2.5,  # 2 Adults + 2 Children
        "parents": 2.2   # Senior parents
    }
    family_factor = family_factors.get(family_type.lower(), 1.0)
    
    # Sum insured factor (higher coverage = lower rate per lakh)
    if sum_insured_lakhs <= 3:
        si_factor = 1.2
    elif sum_insured_lakhs <= 5:
        si_factor = 1.0
    elif sum_insured_lakhs <= 10:
        si_factor = 0.85
    elif sum_insured_lakhs <= 25:
        si_factor = 0.75
    else:
        si_factor = 0.65
    
    # Calculate base premium
    base_premium = sum_insured_lakhs * base_rate_per_lakh * age_factor * family_factor * si_factor
    
    # Add GST (18%)
    premium_with_gst = base_premium * 1.18
    
    # Range (actual premiums can vary ±30% based on insurer, location, etc.)
    premium_low = round(premium_with_gst * 0.7, -2)  # Round to nearest 100
    premium_high = round(premium_with_gst * 1.3, -2)
    premium_mid = round(premium_with_gst, -2)
    
    # Key features at this coverage level
    features = []
    if sum_insured_lakhs >= 5:
        features.append("Room rent likely capped at 1-2% of SI")
    if sum_insured_lakhs >= 10:
        features.append("Usually includes OPD and wellness benefits")
    if sum_insured_lakhs >= 15:
        features.append("Often includes international coverage")
    if sum_insured_lakhs >= 25:
        features.append("Comprehensive coverage with minimal sub-limits")
    
    return {
        "success": True,
        "sum_insured": f"₹{sum_insured_lakhs} Lakhs",
        "family_type": family_type.capitalize(),
        "age": age,
        "estimated_premium": {
            "low": f"₹{int(premium_low):,}",
            "mid": f"₹{int(premium_mid):,}",
            "high": f"₹{int(premium_high):,}",
            "note": "per year (including GST)"
        },
        "typical_features": features if features else ["Basic hospitalization coverage"],
        "recommendations": [
            "Compare at least 3-4 insurers before deciding",
            "Check network hospitals in your city",
            "Review waiting periods for pre-existing conditions",
            "Consider restoration benefit for family plans"
        ],
        "disclaimer": "This is an estimate for guidance. Actual premiums vary by insurer, health status, and policy features."
    }
