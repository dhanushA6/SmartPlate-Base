# Food Recommendation (SmartPlate)

South Indian–focused **meal recommender** that filters foods by health rules, picks items using **macro composition matching**, solves **portion sizes** (LP + fallbacks), and records **like / dislike / skip** feedback so repeat foods can be penalized.

---

## What you need

- **Python 3.10+** (3.11+ recommended)
- Packages: `pandas`, `numpy`, `scipy`, `scikit-learn`

Install from this folder:

```bash
cd New_FoodRecommendation
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Project files


| File                            | Role                                                                                                                 |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `food_recommmender_v3.ipynb`    | Main notebook: `FoodRecommender`, config, demo CLI at the bottom.                                                    |
| `south_indian_food_with_id.csv` | Food catalog (per-100g macros, meal flags, `macro_type`, health flags, `food_id`). **Required** for recommendations. |
| `recommendation_history.csv`    | Append-only feedback log (`user_id`, `food_id`, `date`, `feedback`). Created/updated when you give feedback.         |
| `patient_profiles.csv`          | Example patient rows for experiments (not wired into the interactive demo unless you change the notebook).           |
| `utils_script.ipynb`            | Helper utilities (if any).                                                                                           |


---

## How to run and see output

### 1. Open the notebook

- In VS Code/Cursor: open `food_recommmender_v3.ipynb`.
- Select a Python interpreter that has the dependencies installed.

### 2. Run all cells

Use **Run All** or run cells **top to bottom** at least once so:

- Imports and `CONFIG` load  
- `RecommendationHistory` and `FoodRecommender` are defined  
- `compare_macros` is defined  
- The **last code cell** runs the interactive demo

The last cell uses `if __name__ == "__main__":`. In Jupyter this is usually `__main__`, so that block runs when you execute the cell.

### 3. Provide inputs (prompts): Enter the Detail in the Popup in the Top of Vscode 

The demo prints **Available Users** and asks:

1. `**Enter User ID:`** — e.g. `1` (Dhanush) or `2` (Ravi). These users and their per-meal macro targets are defined **inside the notebook** (not read from `patient_profiles.csv` in the default demo).
2. `**Enter choice:`** for meal type — `1` Breakfast, `2` Lunch, `3` Snacks, `4` Dinner.

### 4. Read the output

You will see, in order:

1. **Welcome** line for the chosen user.
2. `**Recommended <Meal>`** — list of foods with **grams** and **serving unit** (e.g. bowl, piece, tablespoon).
3. `**MACRO COMPARISON`** — target vs actual for carbs, protein, fiber, fat, and calories.
  - Rows marked **✅** are within about **85–115%** of target.  
  - **⚠️** means outside that band.  
  - Calories use **kcal** from the data; the printed line may still say “g” for calories in the demo—interpret the calories row as **kcal**.
4. `**--- Feedback ---`** — for **each** recommended food, enter:
  - `1` = Like  
  - `2` = Dislike  
  - `3` = Skip
5. `**--- Updated History ---`** — full `recommendation_history.csv` table as loaded in memory after feedback (also persisted to disk).

### Example (abbreviated)

```text
Available Users:
  1 → Dhanush
  2 → Ravi

Enter User ID: 2

Welcome Ravi!

Select Meal Type:
  1 → Breakfast
  2 → Lunch
  3 → Snacks
  4 → Dinner
Enter choice: 1

==================================================
Recommended Breakfast
==================================================
  Muttaikose (Cabbage) → 30.0 g (bowl)
  ...

==================================================
MACRO COMPARISON
==================================================
✅ Carbs
   Target  : 50.0 g
   Actual  : 49.4 g
   Achieved: 98.9 %
...
```

---

## How feedback affects future runs

- History is stored in `**recommendation_history.csv**` in this folder.  
- Re-running recommendations uses `**RecommendationHistory**` to add **penalties** for foods shown often or disliked recently, so the same items are less likely to top the list over time.  
- To reset behavior for testing, you can truncate or delete `recommendation_history.csv` (back up first if you care about the log).

---

## Integrating with SmartPlate

- **Macro targets** in production can come from your **LightGBM** (or similar) model instead of the hard-coded `users[...]["targets"]` dict in the notebook.  
- Point `**pd.read_csv(...)`** at your deployed CSV path or load from a database.  
- Keep the same column names expected by `FoodRecommender` (`carb_g`, `protein_g`, `fiber_g`, `fat_g`, `macro_type`, flags, etc.) or adapt the loader once.

---

## Troubleshooting


| Issue                       | What to try                                                                                                                                                                             |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `FileNotFoundError` for CSV | Run the notebook with working directory = `New_FoodRecommendation`, or change `./south_indian_food_with_id.csv` to an absolute path.                                                    |
| Last cell does nothing      | Run all cells above first; execute the last cell again. If `__name__` is not `__main__`, remove the `if __name__ == "__main__":` guard temporarily or run the block without the indent. |
| Empty recommendation        | Health filters may remove all rows; relax vitals in the `users` dict or widen the food table.                                                                                           |


---

## Summary

1. `pip install -r requirements.txt`
2. Open `food_recommmender_v3.ipynb`, **run all cells**
3. In the last cell: **user id** → **meal choice** → read **recommended foods** and **macro comparison** → enter **1/2/3** per food for feedback
4. Inspect `**recommendation_history.csv`** for persisted feedback

