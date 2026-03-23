from typing import Dict, Optional
import random


def mock_food_recommendation(meal_type: str) -> Optional[Dict]:
    meals = {
        "breakfast": [
            {
                "meal": "breakfast",
                "foods": [{
                    "name": "Ragi dosa + mint chutney",
                    "quantity": "2 medium",
                    "calories": 290,
                    "carbs_g": 42,
                    "protein_g": 9,
                    "fat_g": 7,
                    "fiber_g": 6,
                }],
            },
            {
                "meal": "breakfast",
                "foods": [{
                    "name": "Vegetable oats upma",
                    "quantity": "1 bowl",
                    "calories": 280,
                    "carbs_g": 40,
                    "protein_g": 8,
                    "fat_g": 6,
                    "fiber_g": 7,
                }],
            },
            {
                "meal": "breakfast",
                "foods": [{
                    "name": "Kambu (pearl millet) koozh + sundal",
                    "quantity": "1 bowl",
                    "calories": 300,
                    "carbs_g": 45,
                    "protein_g": 10,
                    "fat_g": 6,
                    "fiber_g": 8,
                }],
            },
            {
                "meal": "breakfast",
                "foods": [{
                    "name": "Adai (multigrain dal dosa)",
                    "quantity": "2 small",
                    "calories": 310,
                    "carbs_g": 38,
                    "protein_g": 12,
                    "fat_g": 8,
                    "fiber_g": 7,
                }],
            },
            {
                "meal": "breakfast",
                "foods": [{
                    "name": "Thinai (foxtail millet) pongal",
                    "quantity": "1 bowl",
                    "calories": 300,
                    "carbs_g": 43,
                    "protein_g": 9,
                    "fat_g": 7,
                    "fiber_g": 6,
                }],
            },
        ],

        "lunch": [
            {
                "meal": "lunch",
                "foods": [{
                    "name": "Brown rice + sambar + keerai poriyal",
                    "quantity": "1 plate",
                    "calories": 420,
                    "carbs_g": 55,
                    "protein_g": 16,
                    "fat_g": 9,
                    "fiber_g": 11,
                }],
            },
            {
                "meal": "lunch",
                "foods": [{
                    "name": "Red rice + rasam + cabbage poriyal + curd",
                    "quantity": "1 plate",
                    "calories": 400,
                    "carbs_g": 52,
                    "protein_g": 15,
                    "fat_g": 8,
                    "fiber_g": 10,
                }],
            },
            {
                "meal": "lunch",
                "foods": [{
                    "name": "Millet lemon rice + vegetable kootu",
                    "quantity": "1 plate",
                    "calories": 410,
                    "carbs_g": 50,
                    "protein_g": 14,
                    "fat_g": 10,
                    "fiber_g": 9,
                }],
            },
            {
                "meal": "lunch",
                "foods": [{
                    "name": "Vegetable sambar + 2 phulka (no oil)",
                    "quantity": "1 plate",
                    "calories": 390,
                    "carbs_g": 48,
                    "protein_g": 17,
                    "fat_g": 7,
                    "fiber_g": 12,
                }],
            },
            {
                "meal": "lunch",
                "foods": [{
                    "name": "Curd rice (millet based) + beans poriyal",
                    "quantity": "1 plate",
                    "calories": 430,
                    "carbs_g": 53,
                    "protein_g": 15,
                    "fat_g": 11,
                    "fiber_g": 8,
                }],
            },
        ],

        "snacks": [
            {
                "meal": "snacks",
                "foods": [{
                    "name": "Sundal (boiled channa)",
                    "quantity": "1 cup",
                    "calories": 180,
                    "carbs_g": 22,
                    "protein_g": 9,
                    "fat_g": 4,
                    "fiber_g": 7,
                }],
            },
            {
                "meal": "snacks",
                "foods": [{
                    "name": "Roasted peanuts (unsalted)",
                    "quantity": "30g",
                    "calories": 170,
                    "carbs_g": 6,
                    "protein_g": 7,
                    "fat_g": 14,
                    "fiber_g": 3,
                }],
            },
            {
                "meal": "snacks",
                "foods": [{
                    "name": "Buttermilk + cucumber slices",
                    "quantity": "1 glass + 1 bowl",
                    "calories": 120,
                    "carbs_g": 10,
                    "protein_g": 6,
                    "fat_g": 3,
                    "fiber_g": 2,
                }],
            },
            {
                "meal": "snacks",
                "foods": [{
                    "name": "Sprouts salad",
                    "quantity": "1 bowl",
                    "calories": 160,
                    "carbs_g": 18,
                    "protein_g": 10,
                    "fat_g": 3,
                    "fiber_g": 6,
                }],
            },
            {
                "meal": "snacks",
                "foods": [{
                    "name": "Guava slices + 5 almonds",
                    "quantity": "1 serving",
                    "calories": 150,
                    "carbs_g": 18,
                    "protein_g": 5,
                    "fat_g": 7,
                    "fiber_g": 5,
                }],
            },
        ],

        "dinner": [
            {
                "meal": "dinner",
                "foods": [{
                    "name": "Vegetable kootu + 2 small phulka",
                    "quantity": "1 plate",
                    "calories": 380,
                    "carbs_g": 42,
                    "protein_g": 16,
                    "fat_g": 8,
                    "fiber_g": 10,
                }],
            },
            {
                "meal": "dinner",
                "foods": [{
                    "name": "Millet upma + mixed vegetable curry",
                    "quantity": "1 bowl",
                    "calories": 360,
                    "carbs_g": 40,
                    "protein_g": 14,
                    "fat_g": 7,
                    "fiber_g": 8,
                }],
            },
            {
                "meal": "dinner",
                "foods": [{
                    "name": "Tomato soup + paneer bhurji (low oil)",
                    "quantity": "1 bowl + 1 serving",
                    "calories": 390,
                    "carbs_g": 20,
                    "protein_g": 22,
                    "fat_g": 18,
                    "fiber_g": 6,
                }],
            },
            {
                "meal": "dinner",
                "foods": [{
                    "name": "Ragi kali + keerai masiyal",
                    "quantity": "1 plate",
                    "calories": 370,
                    "carbs_g": 45,
                    "protein_g": 12,
                    "fat_g": 6,
                    "fiber_g": 9,
                }],
            },
            {
                "meal": "dinner",
                "foods": [{
                    "name": "Vegetable stew (coconut light) + 2 small appam (millet)",
                    "quantity": "1 plate",
                    "calories": 400,
                    "carbs_g": 48,
                    "protein_g": 14,
                    "fat_g": 12,
                    "fiber_g": 7,
                }],
            },
        ],
    }

    options = meals.get(meal_type)
    if not options:
        return None

    return random.choice(options)