from typing import Dict


def get_macro_targets() -> Dict:
    return {
        "daily": {
            "calories": 1550,
            "carbs_g": 150,
            "protein_g": 75,
            "fat_g": 55,
            "fiber_g": 38,
        },
        "distribution": {
            "breakfast": 0.25,  # ~390 kcal
            "lunch": 0.35,      # ~540 kcal
            "snacks": 0.15,     # ~230 kcal
            "dinner": 0.25,     # ~390 kcal1
        },
    }


def get_meal_macro_split(meal_type: str) -> Dict:
    macros = get_macro_targets()
    ratio = macros["distribution"][meal_type]
    daily = macros["daily"]

    return {
        "meal": meal_type,
        "calories": daily["calories"] * ratio,
        "carbs_g": daily["carbs_g"] * ratio,
        "protein_g": daily["protein_g"] * ratio,
        "fat_g": daily["fat_g"] * ratio,
        "fiber_g": daily["fiber_g"] * ratio,
    }

