def calculate_targets(age, sex, height_cm, weight_kg, activity, goal):
    # Mifflin-St Jeor estimate.
    if sex == "Male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    factors = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Extra Active": 1.9,
    }
    calories = bmr * factors[activity]

    if goal == "Fat Loss":
        calories *= 0.80
    elif goal == "Muscle Gain":
        calories *= 1.10

    calories = max(1200, round(calories))
    protein = round(weight_kg * (1.8 if goal == "Muscle Gain" else 1.6))
    fat = round((calories * 0.25) / 9)
    carbs = round((calories - protein * 4 - fat * 9) / 4)

    return {
        "calories": calories,
        "protein": max(40, protein),
        "carbs": max(40, carbs),
        "fat": max(30, fat),
        "bmr": round(bmr),
    }

def meal_totals(meal):
    return {
        "calories": float(meal["calories"]),
        "protein": float(meal["protein"]),
        "carbs": float(meal["carbs"]),
        "fat": float(meal["fat"]),
        "fiber": float(meal.get("fiber", 0)),
    }

def daily_totals(df):
    if df.empty:
        return {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}
    return {
        "calories": df["calories"].sum(),
        "protein": df["protein"].sum(),
        "carbs": df["carbs"].sum(),
        "fat": df["fat"].sum(),
        "fiber": df["fiber"].sum() if "fiber" in df else 0,
    }

def recipe_score(meal, targets, meal_count):
    target_cal = targets["calories"] / meal_count
    target_p = targets["protein"] / meal_count
    return (
        abs(meal["calories"] - target_cal) / max(target_cal, 1)
        + abs(meal["protein"] - target_p) / max(target_p, 1)
    )
