import os
import json
import re
from typing import Optional
from pydantic import BaseModel
from google.cloud import documentai
import google.generativeai as genai
from dotenv import load_dotenv

# =====================================================
# LOAD ENV VARIABLES
# =====================================================

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION = os.getenv("GCP_LOCATION")
GCP_PROCESSOR_ID = os.getenv("GCP_PROCESSOR_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

required = {
    "GCP_PROJECT_ID": GCP_PROJECT_ID,
    "GCP_LOCATION": GCP_LOCATION,
    "GCP_PROCESSOR_ID": GCP_PROCESSOR_ID,
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "GOOGLE_APPLICATION_CREDENTIALS": GOOGLE_APPLICATION_CREDENTIALS,
}

missing = [k for k, v in required.items() if not v]
if missing:
    raise Exception(f"Missing required environment variables: {missing}")

if not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
    raise Exception("Service account JSON file not found")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

# =====================================================
# CONFIGURE GEMINI (Stable Model)
# =====================================================

genai.configure(api_key=GEMINI_API_KEY)

# Use supported public model
model = genai.GenerativeModel("gemini-2.5-pro")

# =====================================================
# DATA SCHEMA
# =====================================================

class MedicalSchema(BaseModel):
    age: Optional[float] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    gender: Optional[str] = None
    physical_activity_level: Optional[str] = None
    primary_goal: Optional[str] = None
    steps_per_day: Optional[float] = None
    sleep_hours: Optional[float] = None
    diabetes_duration_years: Optional[float] = None
    hba1c_percent: Optional[float] = None
    fasting_glucose_mg_dl: Optional[float] = None
    postprandial_glucose_mg_dl: Optional[float] = None
    triglycerides_mg_dl: Optional[float] = None
    ldl_cholesterol_mg_dl: Optional[float] = None
    hdl_cholesterol_mg_dl: Optional[float] = None
    systolic_bp_mmHg: Optional[float] = None
    diastolic_bp_mmHg: Optional[float] = None
    creatinine_mg_dl: Optional[float] = None
    egfr_ml_min_1_73m2: Optional[float] = None
    smoking_status: Optional[int] = 0
    alcohol_use: Optional[int] = 0


# =====================================================
# DOCUMENT AI OCR FUNCTION
# =====================================================

def extract_text_with_ocr(file_path: str) -> str:
    try:
        client = documentai.DocumentProcessorServiceClient()

        processor_name = client.processor_path(
            GCP_PROJECT_ID,
            GCP_LOCATION,
            GCP_PROCESSOR_ID,
        )

        with open(file_path, "rb") as f:
            file_content = f.read()

        raw_document = documentai.RawDocument(
            content=file_content,
            mime_type="application/pdf",
        )

        request = documentai.ProcessRequest(
            name=processor_name,
            raw_document=raw_document,
        )

        result = client.process_document(request=request)

        print("✅ OCR extraction successful\n")

        return result.document.text

    except Exception as e:
        print("❌ Document AI Error:")
        raise e


# =====================================================
# GEMINI STRUCTURED EXTRACTION
# =====================================================

def extract_with_gemini(text: str) -> dict:
    schema_template = MedicalSchema().model_dump()

    prompt = f"""
You are a strict medical data extraction system.

Rules:
- Extract ONLY explicitly mentioned values.
- Do NOT calculate.
- Do NOT assume.
- Missing values must be null.
- Return ONLY valid JSON.
- No explanation text.

Schema:
{json.dumps(schema_template, indent=2)}

Medical Report:
{text}
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0,
            "response_mime_type": "application/json"
        }
    )

    try:
        parsed = json.loads(response.text)
        print("✅ Gemini extraction successful\n")
        return parsed
    except json.JSONDecodeError:
        print("❌ Gemini returned invalid JSON")
        print(response.text)
        raise


# =====================================================
# NORMALIZATION
# =====================================================

def normalize_output(data: dict) -> dict:
    for key, value in list(data.items()):
        if isinstance(value, str):

            clean = (
                value.replace("%", "")
                .replace("mg/dL", "")
                .replace("mmHg", "")
                .strip()
            )

            # Handle blood pressure format (120/80)
            bp_match = re.match(r"(\d+)\s*/\s*(\d+)", clean)
            if bp_match:
                data["systolic_bp_mmHg"] = float(bp_match.group(1))
                data["diastolic_bp_mmHg"] = float(bp_match.group(2))
                continue

            try:
                data[key] = float(clean)
            except:
                data[key] = clean

    return data


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    FILE_PATH = r".\Diabetic_Medical_Report.pdf"

    if not os.path.exists(FILE_PATH):
        raise Exception("File not found")

    print("\n🚀 Processing Document...\n")

    # Step 1: OCR
    extracted_text = extract_text_with_ocr(FILE_PATH)

    # Step 2: Structured extraction via Gemini
    structured_data = extract_with_gemini(extracted_text)

    # Step 3: Normalize values
    normalized = normalize_output(structured_data)

    # Step 4: Validate with Pydantic
    validated = MedicalSchema(**normalized)

    print("\n🎯 FINAL STRUCTURED OUTPUT:\n")
    print(json.dumps(validated.model_dump(), indent=4))