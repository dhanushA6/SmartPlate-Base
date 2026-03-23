# Report Suitability Modules

This folder contains utility modules used in SmartPlate for two core tasks:

1. Extract user medical parameters from uploaded medical reports.
2. Evaluate food suitability for diabetes care and classify each food as:
   - Suitable
   - Moderate
   - Not Suitable (No Suitable)

## Purpose in SmartPlate

These modules are helper components for the SmartPlate application flow:

- report-processor.py:
  - Reads a PDF medical report.
  - Uses Google Document AI for OCR text extraction.
  - Uses Gemini to map extracted values into a structured medical profile.

- food-sutability.py:
  - Runs a rule-based food suitability engine using patient profile, meal targets, and nutrition values.
  - Produces food-level and meal-level suitability outputs.

Important integration note:
- In the current driver code, food nutrition values are provided manually.
- In SmartPlate production flow, nutrition should come from INDB and then be passed to this engine.

## Folder Structure

- .env
- .env.example
- Anuvaad_INDB_2024.11.xlsx
- Diabetic_Medical_Report.pdf
- food-sutability.py
- README.md
- report-processor.py
- requirements.txt

## Prerequisites

- Python 3.9+
- Google Cloud Document AI processor
- Gemini API key
- Google service account JSON with Document AI access

## Installation

Run from this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Environment Configuration

Create a .env file (or copy from .env.example) and fill values:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GCP_PROJECT_ID=your_gcp_project_id
GCP_LOCATION=your_gcp_location
GCP_PROCESSOR_ID=your_document_ai_processor_id
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account.json
```

## Usage

### 1) Extract Medical Parameters from Report

Input:
- PDF report file (default in script: Diabetic_Medical_Report.pdf)

Gemini SDK import used in code:

```python
import google.generativeai as genai
```

Reference:
- https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md

Run:

```powershell
python .\report-processor.py
```

Output:
- Structured medical profile printed as JSON.

Sample CLI output:

```text
🚀 Processing Document...

✅ OCR extraction successful

✅ Gemini extraction successful


🎯 FINAL STRUCTURED OUTPUT:

{
  "age": 52.0,
  "height_cm": 170.0,
  "weight_kg": 78.0,
  "bmi": null,
  "gender": "Male",
  "physical_activity_level": null,
  "primary_goal": null,
  "steps_per_day": null,
  "sleep_hours": null,
  "diabetes_duration_years": null,
  "hba1c_percent": 8.1,
  "fasting_glucose_mg_dl": 168.0,
  "postprandial_glucose_mg_dl": 245.0,
  "triglycerides_mg_dl": 220.0,
  "ldl_cholesterol_mg_dl": 138.0,
  "hdl_cholesterol_mg_dl": 36.0,
  "systolic_bp_mmHg": 148.0,
  "diastolic_bp_mmHg": 94.0,
  "creatinine_mg_dl": null,
  "egfr_ml_min_1_73m2": 75.0,
  "smoking_status": null,
  "alcohol_use": null
}
```

### 2) Food Suitability Classification

Run:

```powershell
python .\food-sutability.py
```

Output includes:
- Food-level suitability
- Meal-level analysis
- Final overall suitability
- User-friendly response summary

## Integration Guide for SmartPlate

Recommended runtime sequence:

1. Process user report with report-processor.py to get medical parameters.
2. Fetch food nutrition from INDB in SmartPlate.
3. Map INDB nutrients into FoodNutrients structure.
4. Build FoodItem list and patient profile.
5. Call FoodSuitabilityEngine.evaluate(...).
6. Show labels and reasons in UI.

## Classification Labels

- Suitable: safe choice for the current profile and meal targets.
- Moderate: acceptable with portion/frequency control.
- Not Suitable (No Suitable): high risk for the current profile.

## Notes

- food-sutability.py filename is kept as-is to match the current project naming.
- If OCR fails, verify GCP credentials, project, location, and processor ID.
- If extraction is empty, verify PDF quality and processor type.

## Dependencies

From requirements.txt:

- google-generativeai
- google-cloud-documentai
- python-dotenv
- pydantic>=2
