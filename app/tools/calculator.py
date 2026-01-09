"""
Calculator Tools
Calorie calculator with Indian food database and BMI calculator
"""
from typing import Dict, Optional

# Indian food calorie database (per 100g or per serving as noted)
INDIAN_FOOD_DATABASE = {
    # Grains & Breads
    "roti": {"calories": 120, "serving": "1 piece", "protein": 3, "carbs": 20, "fat": 3},
    "chapati": {"calories": 120, "serving": "1 piece", "protein": 3, "carbs": 20, "fat": 3},
    "naan": {"calories": 260, "serving": "1 piece", "protein": 9, "carbs": 45, "fat": 5},
    "paratha": {"calories": 200, "serving": "1 piece", "protein": 4, "carbs": 30, "fat": 7},
    "rice": {"calories": 130, "serving": "100g cooked", "protein": 2.7, "carbs": 28, "fat": 0.3},
    "biryani": {"calories": 250, "serving": "100g", "protein": 8, "carbs": 35, "fat": 8},
    "pulao": {"calories": 180, "serving": "100g", "protein": 4, "carbs": 30, "fat": 5},
    "dosa": {"calories": 120, "serving": "1 plain", "protein": 3, "carbs": 18, "fat": 4},
    "idli": {"calories": 40, "serving": "1 piece", "protein": 1.5, "carbs": 8, "fat": 0.2},
    "upma": {"calories": 150, "serving": "100g", "protein": 4, "carbs": 22, "fat": 5},
    "poha": {"calories": 180, "serving": "100g", "protein": 3, "carbs": 30, "fat": 5},
    
    # Dals & Legumes
    "dal": {"calories": 110, "serving": "100g cooked", "protein": 7, "carbs": 15, "fat": 2},
    "rajma": {"calories": 130, "serving": "100g cooked", "protein": 8, "carbs": 20, "fat": 1},
    "chole": {"calories": 160, "serving": "100g cooked", "protein": 9, "carbs": 25, "fat": 3},
    "chana": {"calories": 160, "serving": "100g cooked", "protein": 9, "carbs": 25, "fat": 3},
    "sambar": {"calories": 80, "serving": "100g", "protein": 4, "carbs": 12, "fat": 2},
    
    # Vegetables
    "palak paneer": {"calories": 200, "serving": "100g", "protein": 10, "carbs": 8, "fat": 15},
    "paneer": {"calories": 265, "serving": "100g", "protein": 18, "carbs": 1.2, "fat": 21},
    "aloo gobi": {"calories": 120, "serving": "100g", "protein": 3, "carbs": 15, "fat": 5},
    "bhindi": {"calories": 80, "serving": "100g", "protein": 2, "carbs": 10, "fat": 3},
    "baingan": {"calories": 100, "serving": "100g", "protein": 2, "carbs": 12, "fat": 5},
    "mixed veg": {"calories": 100, "serving": "100g", "protein": 3, "carbs": 12, "fat": 4},
    
    # Non-Veg
    "chicken curry": {"calories": 180, "serving": "100g", "protein": 20, "carbs": 5, "fat": 10},
    "butter chicken": {"calories": 250, "serving": "100g", "protein": 18, "carbs": 8, "fat": 17},
    "fish curry": {"calories": 150, "serving": "100g", "protein": 18, "carbs": 4, "fat": 7},
    "egg": {"calories": 80, "serving": "1 boiled", "protein": 6, "carbs": 0.5, "fat": 5},
    "egg curry": {"calories": 150, "serving": "100g", "protein": 10, "carbs": 6, "fat": 10},
    
    # Snacks
    "samosa": {"calories": 250, "serving": "1 piece", "protein": 4, "carbs": 25, "fat": 15},
    "pakora": {"calories": 150, "serving": "5 pieces", "protein": 3, "carbs": 15, "fat": 9},
    "vada pav": {"calories": 300, "serving": "1 piece", "protein": 6, "carbs": 40, "fat": 12},
    "pav bhaji": {"calories": 400, "serving": "1 plate", "protein": 10, "carbs": 50, "fat": 18},
    
    # Drinks
    "chai": {"calories": 100, "serving": "1 cup", "protein": 3, "carbs": 12, "fat": 4},
    "lassi": {"calories": 150, "serving": "1 glass", "protein": 5, "carbs": 20, "fat": 5},
    "buttermilk": {"calories": 40, "serving": "1 glass", "protein": 2, "carbs": 5, "fat": 1},
    
    # Sweets
    "gulab jamun": {"calories": 150, "serving": "1 piece", "protein": 2, "carbs": 25, "fat": 5},
    "rasgulla": {"calories": 120, "serving": "1 piece", "protein": 3, "carbs": 22, "fat": 2},
    "jalebi": {"calories": 150, "serving": "1 piece", "protein": 1, "carbs": 30, "fat": 4},
    "kheer": {"calories": 180, "serving": "100g", "protein": 5, "carbs": 28, "fat": 6},
}


def calculate_calories(food_item: str, quantity: float = 1) -> Dict:
    """
    Calculate calories for an Indian food item
    
    Args:
        food_item: Name of the food item
        quantity: Number of servings or multiplier for 100g items
    
    Returns:
        Dict with calories, macros, and serving info
    """
    food_lower = food_item.lower().strip()
    
    # Try exact match
    if food_lower in INDIAN_FOOD_DATABASE:
        food = INDIAN_FOOD_DATABASE[food_lower]
        return {
            "success": True,
            "food": food_item,
            "serving_size": food["serving"],
            "quantity": quantity,
            "calories": round(food["calories"] * quantity),
            "protein": round(food["protein"] * quantity, 1),
            "carbs": round(food["carbs"] * quantity, 1),
            "fat": round(food["fat"] * quantity, 1),
            "source": "VEDA Indian Food Database"
        }
    
    # Try partial match
    for key, food in INDIAN_FOOD_DATABASE.items():
        if key in food_lower or food_lower in key:
            return {
                "success": True,
                "food": key,
                "serving_size": food["serving"],
                "quantity": quantity,
                "calories": round(food["calories"] * quantity),
                "protein": round(food["protein"] * quantity, 1),
                "carbs": round(food["carbs"] * quantity, 1),
                "fat": round(food["fat"] * quantity, 1),
                "source": "VEDA Indian Food Database"
            }
    
    # Not found
    return {
        "success": False,
        "food": food_item,
        "message": f"'{food_item}' not found in database. Available items include: dosa, idli, roti, dal, paneer, biryani, and more."
    }


def calculate_bmi(height_cm: float, weight_kg: float) -> Dict:
    """
    Calculate BMI and provide health category
    
    Args:
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
    
    Returns:
        Dict with BMI, category, and recommendations
    """
    if height_cm <= 0 or weight_kg <= 0:
        return {
            "success": False,
            "message": "Height and weight must be positive numbers"
        }
    
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    bmi_rounded = round(bmi, 1)
    
    # Determine category (Asian BMI standards, slightly lower thresholds)
    if bmi < 18.5:
        category = "Underweight"
        recommendation = "Consider consulting a dietitian for healthy weight gain strategies."
    elif 18.5 <= bmi < 23:
        category = "Normal (Healthy)"
        recommendation = "Great! Maintain your healthy weight with balanced diet and regular exercise."
    elif 23 <= bmi < 25:
        category = "Overweight (Pre-obese)"
        recommendation = "Slight risk. Consider reducing refined carbs and increasing physical activity."
    elif 25 <= bmi < 30:
        category = "Obese Class I"
        recommendation = "Moderate risk. Focus on sustainable weight loss through diet and exercise."
    else:
        category = "Obese Class II+"
        recommendation = "Higher health risk. Please consult a doctor for personalized guidance."
    
    # Calculate healthy weight range
    healthy_weight_min = round(18.5 * (height_m ** 2), 1)
    healthy_weight_max = round(23 * (height_m ** 2), 1)
    
    return {
        "success": True,
        "bmi": bmi_rounded,
        "category": category,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "healthy_weight_range": f"{healthy_weight_min} - {healthy_weight_max} kg",
        "recommendation": recommendation,
        "note": "BMI is a screening tool. Consult a doctor for complete assessment."
    }
