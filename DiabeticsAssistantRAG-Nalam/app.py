import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from nalam_retriever import NalamRetriever
from nalam_generator import NalamGenerator
from nalam_risk_engine import RiskAnalyzer, UserProfile
from typing import Any, Dict, Optional, List

from config import GOOGLE_API_KEY
from macro_engine import get_macro_targets, get_meal_macro_split
from food_recommendations import mock_food_recommendation

app = FastAPI(title="Nalam RAG API", description="Health Assistant with Risk Analysis")

# --- GLOBAL INSTANCES (Load once on startup) ---
retriever = None
generator = None

GEMINI_API_KEY = GOOGLE_API_KEY


def _compact_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


def _has_any_medical_data(medical_dict: Dict[str, Any]) -> bool:
    return bool(medical_dict)


@app.on_event("startup")
def startup_event():
    global retriever, generator
    print("🚀 Starting Nalam API...")
    
    # Check for API Key
    if not GEMINI_API_KEY:
        print("⚠️ WARNING: GEMINI_API_KEY not found in environment variables!")
    
    # Initialize Core Modules1
    # Note: We assume the DB folder is copied into the Docker container at /app/nalam_chroma_db
    retriever = NalamRetriever(db_path="./nalam_chroma_db")
    generator = NalamGenerator(api_key=GEMINI_API_KEY)
    print("✅ System Ready.")

# --- REQUEST MODEL ---
class DietRequest(BaseModel):
    # Required
    question: str

    # Mode routing
    mode: str = "normal"  # "normal" | "food_recommendation"
    meal_type: Optional[str] = None  # required only when mode="food_recommendation"

    # Optional medical parameters
    hba1c_percent: Optional[float] = None
    fasting_glucose_mg_dl: Optional[float] = None
    post_prandial_glucose_mg_dl: Optional[float] = None
    hypoglycemia_history: Optional[bool] = None
    diabetes_duration_years: Optional[int] = None
    ldl_cholesterol_mg_dl: Optional[float] = None
    hdl_cholesterol_mg_dl: Optional[float] = None
    triglycerides_mg_dl: Optional[float] = None
    systolic_bp_mmHg: Optional[float] = None
    diastolic_bp_mmHg: Optional[float] = None
    eGFR: Optional[float] = None
    creatinine_mg_dl: Optional[float] = None
    bmi: Optional[float] = None

    # Optional non-medical parameters (lifestyle / preferences)
    age_years: Optional[int] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    dietary_preference: Optional[str] = None
    allergies: Optional[List[str]] = []
    goal: Optional[str] = None
  
    

# --- API ENDPOINT ---
@app.post("/ask_nalam")
async def ask_nalam(request: DietRequest):
    if not retriever or not generator:
        raise HTTPException(status_code=503, detail="System initializing...")

    try:
        mode = (request.mode or "normal").strip().lower()

        # Step A: Build extended profile context (only non-None values)
        medical_dict = _compact_dict(
            {
                "hba1c_percent": request.hba1c_percent,
                "fasting_glucose_mg_dl": request.fasting_glucose_mg_dl,
                "post_prandial_glucose_mg_dl": request.post_prandial_glucose_mg_dl,
                "hypoglycemia_history": request.hypoglycemia_history,
                "diabetes_duration_years": request.diabetes_duration_years,
                "ldl_cholesterol_mg_dl": request.ldl_cholesterol_mg_dl,
                "hdl_cholesterol_mg_dl": request.hdl_cholesterol_mg_dl,
                "triglycerides_mg_dl": request.triglycerides_mg_dl,
                "systolic_bp_mmHg": request.systolic_bp_mmHg,
                "diastolic_bp_mmHg": request.diastolic_bp_mmHg,
                "eGFR": request.eGFR,
                "creatinine_mg_dl": request.creatinine_mg_dl,
                "bmi": request.bmi,
            }
        )

        lifestyle_dict = _compact_dict(
            {
                "age_years": request.age_years,
                "sex": request.sex,
                "height_cm": request.height_cm,
                "weight_kg": request.weight_kg,
                "activity_level": request.activity_level,
                "dietary_preference": request.dietary_preference,
                "allergies": request.allergies,
                "goal": request.goal,
            
            }
        )

        # Macros are always included (both modes, per spec)
        macro_targets = get_macro_targets()

        if mode == "food_recommendation":
            # Step B (food mode): validate meal_type and inject mock food recommendation
            if not request.meal_type:
                raise HTTPException(status_code=400, detail="meal_type is required when mode='food_recommendation'")

            meal_type = request.meal_type.strip().lower()
            if meal_type not in macro_targets["distribution"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid meal_type '{meal_type}'. Must be one of: {list(macro_targets['distribution'].keys())}",
                )

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
                user_question=request.question,
                risk_profile=None,
                structured_context=structured_context,
            )

            return {
                "status": "success",
                "mode": mode,
                "meal_type": meal_type,
                "answer": answer,
                "macro_targets": structured_context["macro_targets"],
                "food_recommendation": food_rec,
            }

        # Step B (normal mode): retrieval + (optional) risk + full meal splits
        meal_splits = {m: get_meal_macro_split(m) for m in macro_targets["distribution"].keys()}

        risk_profile = None
        if _has_any_medical_data(medical_dict):
            # All fields in UserProfile are optional now, so we can safely pass
            # only the keys we actually have from the request.
            user_profile = UserProfile(**medical_dict)  # type: ignore[arg-type]
            risk_profile = RiskAnalyzer.analyze(user_profile)

        retrieved_context = retriever.get_relevant_context(request.question)

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
            retrieved_context,
            request.question,
            risk_profile=risk_profile,
            structured_context=structured_context,
        )

        return {
            "status": "success",
            "mode": mode,
            "risk_analysis": risk_profile,
            "answer": answer,
            "retrieved_context_preview": retrieved_context[:200] + "..." if retrieved_context else "None",
            "macro_targets": structured_context["macro_targets"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/")
def home():
    return {"message": "Nalam RAG API is running. Use /ask_nalam endpoint."}