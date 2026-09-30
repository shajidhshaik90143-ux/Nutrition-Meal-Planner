# Nutrition Meal Planner

A strong Streamlit nutrition planning application with:

- Personal calorie and macro target estimation
- Mifflin-St Jeor BMR calculation
- Activity and goal adjustments
- 7-day automated meal planner
- Vegetarian, vegan, high-protein and low-carb filters
- Allergy/ingredient exclusion
- Meal library search
- Custom meal creation
- SQLite persistence
- Nutrition dashboard and charts
- CSV and JSON export
- Deterministic planner seed
- Clean modular Python architecture

## Project Structure

```text
Nutrition Meal Planner/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── .gitkeep
└── src/
    ├── __init__.py
    ├── database.py
    ├── exporter.py
    ├── meals.py
    ├── nutrition.py
    └── planner.py
```

## Windows Setup

Open PowerShell in the project folder:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Then open the Streamlit URL shown in the terminal, normally:

```text
http://localhost:8501
```

## Features

### Dashboard
Displays estimated daily calories and macro targets, plus plan-level charts.

### Weekly Planner
Generates a 7-day plan according to:
- calorie target
- protein target
- dietary preference
- allergy exclusions
- meals per day
- planner seed

### Meal Library
Search and filter meals by calories, protein and diet.

### Custom Meal
Add your own meals. They are stored in SQLite and become available to the planner.

### Export
Download the current weekly plan as CSV or JSON.

## Notes

This application provides estimates for educational planning. It is not medical advice and should not be used to diagnose or treat a medical condition. Individual nutrition needs can vary substantially.
