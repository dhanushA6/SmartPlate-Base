# MacroNutritionPrediction

Clinical nutrition macro prediction workspace for diabetes-focused modeling and analysis.

## Prerequisites

- Python 3.10 or newer
- pip
- Jupyter Notebook or VS Code with Jupyter extension

## Project Contents

- `EDA_diabetics_Data.ipynb` - exploratory analysis workflow
- `macro_prediction_diabetics.ipynb` - model training and comparison workflow
- `userData.csv` - input dataset used by notebooks
- `model_comparison_results.csv` - saved model comparison output
- `predicted_nutrition_results.csv` - saved prediction output
- `weights/` - model artifacts/checkpoints
- `requirements.txt` - Python dependencies

## Quick Start

### 1) Open terminal in this folder

```powershell
cd "c:\Users\gokul\Documents\Dhanush_Work\SmartPlate-Base\MacroNutritionPrediction"
```

### 2) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run once:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again.

### 3) Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Start Jupyter

```powershell
jupyter notebook
```

### 5) Run notebooks in this order

1. `EDA_diabetics_Data.ipynb`
2. `macro_prediction_diabetics.ipynb`

## Running in VS Code

1. Open this folder in VS Code.
2. Select the `.venv` Python interpreter.
3. Open each notebook and run all cells.

## Notes

- `weights/` is expected to be empty initially.
- Run `macro_prediction_diabetics.ipynb` once for first-time setup so required artifacts are generated (typically takes about 5-10 minutes).
- Keep `weights/` inside this folder so notebook paths resolve correctly.
- If `faiss-cpu` install fails on your machine, update pip first and retry.
- If kernel issues appear, reinstall kernel support:

```powershell
pip install ipykernel
python -m ipykernel install --user --name macro-nutrition
```

## Troubleshooting

- `ModuleNotFoundError`: confirm environment is activated and run `pip install -r requirements.txt` again.
- Notebook kernel not visible: restart VS Code and reselect interpreter.
- Slow first run for transformers models is normal due to initial download/cache.
