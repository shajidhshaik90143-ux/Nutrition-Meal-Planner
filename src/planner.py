import random
from datetime import date, timedelta
from src.meals import MEALS
from src.nutrition import recipe_score

ALLERGY_MAP = {
    "Peanuts": ["peanut"],
    "Tree Nuts": ["almond", "cashew", "walnut", "nut"],
    "Dairy": ["milk", "yogurt", "paneer", "cheese"],
    "Eggs": ["egg"],
    "Gluten": ["wheat", "roti", "semolina"],
    "Soy": ["soy", "tofu"],
    "Fish": ["fish"],
    "Shellfish": ["shrimp", "prawn", "shellfish"],
}

def allowed(meal, dietary, allergies, min_protein):
    if dietary == "Vegetarian" and meal["diet"] not in ("Vegetarian", "Vegan"):
        return False
    if dietary == "Vegan" and meal["diet"] != "Vegan":
        return False
    if dietary == "High Protein" and meal["protein"] < min_protein:
        return False
    if dietary == "Low Carb" and meal["carbs"] > 45:
        return False

    text = " ".join(meal["ingredients"]).lower()
    for allergy in allergies:
        if any(x in text for x in ALLERGY_MAP.get(allergy, [])):
            return False
    return True

def build_week_plan(targets, meals_per_day, dietary, allergies, min_protein, custom_meals, seed=42):
    rng = random.Random(seed)
    pool = MEALS + custom_meals
    pool = [m for m in pool if allowed(m, dietary, allergies, min_protein)]
    if not pool:
        pool = [m for m in MEALS if not allergies or allowed(m, "All", allergies, min_protein)]

    meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
    if meals_per_day == 3:
        meal_types = ["Breakfast", "Lunch", "Dinner"]
    elif meals_per_day == 5:
        meal_types = ["Breakfast", "Snack", "Lunch", "Dinner", "Snack"]
    elif meals_per_day == 6:
        meal_types = ["Breakfast", "Snack", "Lunch", "Snack", "Dinner", "Snack"]

    plan = {}
    start = date.today()
    used_recent = []

    for d in range(7):
        day_name = (start + timedelta(days=d)).strftime("%A")
        day_plan = []
        for mt in meal_types:
            candidates = [m for m in pool if m["meal_type"] == mt]
            if not candidates:
                candidates = pool

            candidates = sorted(
                candidates,
                key=lambda m: recipe_score(m, targets, meals_per_day) + rng.random() * 0.18
            )
            chosen = next((m for m in candidates if m["name"] not in used_recent[-4:]), candidates[0])
            used_recent.append(chosen["name"])

            day_plan.append(dict(chosen))
        plan[day_name] = day_plan

    return plan

def flatten_plan(plan):
    rows = []
    for day, meals in plan.items():
        for meal in meals:
            row = dict(meal)
            row["day"] = day
            row["ingredients"] = ", ".join(meal.get("ingredients", []))
            rows.append(row)
    return rows
