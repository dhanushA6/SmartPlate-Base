from nalam_retriever import NalamRetriever
from nalam_generator import NalamGenerator
from nalam_risk_engine import RiskAnalyzer, UserProfile
from typing import Any, Dict, Optional

from config import GOOGLE_API_KEY
from macro_engine import get_macro_targets, get_meal_macro_split
from food_recommendations import mock_food_recommendation

GEMINI_API_KEY = GOOGLE_API_KEY

# --- MOCK DATA FOR TESTING ---
def get_mock_user(profile_type):
    if profile_type == "1":
        return UserProfile(
    # Moderate diabetes control (Not great, but not dangerously high)
            hba1c_percent=7.4, 
            fasting_glucose_mg_dl=135, 
            post_prandial_glucose_mg_dl=190,
            hypoglycemia_history=False, 
            diabetes_duration_years=5,

            # Borderline cholesterol issues
            ldl_cholesterol_mg_dl=130, 
            hdl_cholesterol_mg_dl=40, 
            triglycerides_mg_dl=165,

            # Mild blood pressure (Stage 1 Hypertension)
            systolic_bp_mmHg=130, 
            diastolic_bp_mmHg=85,

            # Perfectly normal kidney function (No kidney issues)
            eGFR=95, 
            creatinine_mg_dl=0.9, 

            # Corrected physical metrics for a "weight loss" goal
            age_years=40, 
            sex="male", 
            height_cm=170, 
            weight_kg=82,  # Adjusted to match the overweight BMI
            bmi=28.4,      # Calculated as 82 / (1.7 * 1.7)
            
            # Lifestyle and preferences
            activity_level="sedentary", 
            dietary_preference="vegetarian", 
            allergies=[], 
            goal="weight loss"
        )
    else:
        # Healthy / Controlled
        return UserProfile(
            hba1c_percent=6.4, fasting_glucose_mg_dl=105, post_prandial_glucose_mg_dl=140,
            hypoglycemia_history=False, diabetes_duration_years=3,
            ldl_cholesterol_mg_dl=110, hdl_cholesterol_mg_dl=50, triglycerides_mg_dl=120,
            systolic_bp_mmHg=118, diastolic_bp_mmHg=75,
            eGFR=95, creatinine_mg_dl=0.9, bmi=23, age_years=30, sex="female", height_cm=160, weight_kg=60, activity_level="moderate", dietary_preference="vegetarian", allergies=[], goal="maintenance"
        )

def _has_sufficient_medical_data(medical_dict: Dict[str, Any]) -> bool:
    required = [
        "hba1c_percent",
        "fasting_glucose_mg_dl",
        "post_prandial_glucose_mg_dl",
        "hypoglycemia_history",
        "diabetes_duration_years",
        "ldl_cholesterol_mg_dl",
        "hdl_cholesterol_mg_dl",
        "triglycerides_mg_dl",
        "systolic_bp_mmHg",
        "diastolic_bp_mmHg",
        "eGFR",
        "creatinine_mg_dl",
        "bmi",
    ]
    return all(k in medical_dict for k in required)


def _userprofile_to_medical_dict(user: UserProfile) -> Dict[str, Any]:
    return {
        "hba1c_percent": user.hba1c_percent,
        "fasting_glucose_mg_dl": user.fasting_glucose_mg_dl,
        "post_prandial_glucose_mg_dl": user.post_prandial_glucose_mg_dl,
        "hypoglycemia_history": user.hypoglycemia_history,
        "diabetes_duration_years": user.diabetes_duration_years,
        "ldl_cholesterol_mg_dl": user.ldl_cholesterol_mg_dl,
        "hdl_cholesterol_mg_dl": user.hdl_cholesterol_mg_dl,
        "triglycerides_mg_dl": user.triglycerides_mg_dl,
        "systolic_bp_mmHg": user.systolic_bp_mmHg,
        "diastolic_bp_mmHg": user.diastolic_bp_mmHg,
        "eGFR": user.eGFR,
        "creatinine_mg_dl": user.creatinine_mg_dl,
        "bmi": user.bmi,
    }
def _userprofile_to_lifestyle_dict(user: UserProfile) -> Dict[str, Any]:
    return {
        "age_years": user.age_years,
        "sex": user.sex,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "activity_level": user.activity_level,
        "dietary_preference": user.dietary_preference,
    }
    return lifestyle_dict

def main():
    # 1. Initialize System
    try:
        retriever = NalamRetriever()
        generator = NalamGenerator(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        return

    # 2. Load User Profile
    print("\n📋 --- PATIENT PROFILE SELECTION ---")
    print("1. Case A: High Risk (Uncontrolled Diabetes, Kidney Issues)")
    print("2. Case B: Well Controlled (Healthy)")
    print("3. No medical profile (skip RiskAnalyzer)")
    choice = input("Select User Profile (1/2/3): ").strip()

    current_user: Optional[UserProfile] = None
    medical_dict: Dict[str, Any] = {}
    if choice in ["1", "2"]:
        current_user = get_mock_user(choice)
        medical_dict = _userprofile_to_medical_dict(current_user)

    lifestyle_dict: Dict[str, Any] = _userprofile_to_lifestyle_dict(current_user) if current_user else {}

    macro_targets = get_macro_targets()
    
    print("\n🥗 --- NALAM RAG READY --- 🥗")
    print("(Type 'quit' to exit)")

    # 4. Chat Loop
    while True:
        mode = input("\nMode (normal/food_recommendation) [normal]: ").strip().lower() or "normal"
        meal_type = None
        if mode == "food_recommendation":
            meal_type = input("Meal type (breakfast/lunch/snacks/dinner): ").strip().lower()

        user_query = input("\n👤 You: ")
        
        if user_query.lower() in ["quit", "exit"]:
            break

        if mode == "food_recommendation":
            if not meal_type:
                print("❌ meal_type is required for food_recommendation mode.")
                continue
            if meal_type not in macro_targets["distribution"]:
                print(f"❌ Invalid meal_type '{meal_type}'.")
                continue

            meal_macro_split = get_meal_macro_split(meal_type)
            food_rec = mock_food_recommendation(meal_type)

            structured_context = {
                "mode": mode,
                "user_profile": {"medical": medical_dict, "lifestyle": lifestyle_dict},
                "macro_targets": {
                    "daily": macro_targets["daily"],
                    "distribution": macro_targets["distribution"],
                    "meal": meal_macro_split,
                },
                "food_recommendation": food_rec,
            }

            answer = generator.generate_response(
                context="",
                user_question=user_query,
                risk_profile=None,
                structured_context=structured_context,
            )

            print(f"\n🤖 Nalam: {answer}")
            print("-" * 50)
            continue

        meal_splits = {m: get_meal_macro_split(m) for m in macro_targets["distribution"].keys()}

        risk_profile = None
        if _has_sufficient_medical_data(medical_dict) and current_user is not None:
            risk_profile = RiskAnalyzer.analyze(current_user)

        context_data = retriever.get_relevant_context(user_query)

        structured_context = {
            "mode": mode,
            "user_profile": {"medical": medical_dict, "lifestyle": lifestyle_dict},
            "risk_analysis": risk_profile,
            "macro_targets": {
                "daily": macro_targets["daily"],
                "distribution": macro_targets["distribution"],
                "meal_splits": meal_splits,
            },
        }

        answer = generator.generate_response(
            context_data,
            user_query,
            risk_profile=risk_profile,
            structured_context=structured_context,
        )

        print(f"\n🤖 Nalam: {answer}")
        print("-" * 50)

if __name__ == "__main__":
    main()