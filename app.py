import json
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from src.database import (
    init_db, add_custom_meal, get_custom_meals, delete_custom_meal,
    save_plan, load_plan, clear_plan
)
from src.nutrition import calculate_targets, meal_totals, daily_totals, recipe_score
from src.planner import build_week_plan, flatten_plan
from src.exporter import dataframe_to_csv, plan_to_json

st.set_page_config(page_title="Nutrition Meal Planner", page_icon="🥗", layout="wide")

init_db()

if "plan" not in st.session_state:
    st.session_state.plan = load_plan()

st.title("🥗 Nutrition Meal Planner")
st.caption("A complete meal-planning dashboard for calorie targets, macros, weekly meals, custom recipes, and exports.")

with st.sidebar:
    st.header("Profile & Goals")
    age = st.number_input("Age", 12, 100, 21)
    sex = st.selectbox("Sex", ["Male", "Female"])
    height = st.number_input("Height (cm)", 100.0, 230.0, 170.0)
    weight = st.number_input("Weight (kg)", 30.0, 250.0, 70.0)
    activity = st.selectbox(
        "Activity level",
        ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"]
    )
    goal = st.selectbox("Goal", ["Maintain Weight", "Fat Loss", "Muscle Gain"])
    dietary = st.selectbox(
        "Diet preference",
        ["All", "Vegetarian", "Vegan", "High Protein", "Low Carb"]
    )
    allergies = st.multiselect(
        "Avoid ingredients",
        ["Peanuts", "Tree Nuts", "Dairy", "Eggs", "Gluten", "Soy", "Fish", "Shellfish"]
    )
    target_protein = st.slider("Minimum protein per meal (g)", 5, 60, 20)

targets = calculate_targets(age, sex, height, weight, activity, goal)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Daily Calories", f"{targets['calories']:,} kcal")
c2.metric("Protein", f"{targets['protein']} g")
c3.metric("Carbs", f"{targets['carbs']} g")
c4.metric("Fat", f"{targets['fat']} g")

tabs = st.tabs(["📊 Dashboard", "🗓️ Weekly Planner", "🍽️ Meal Library", "➕ Custom Meal", "📤 Export"])

with tabs[0]:
    st.subheader("Daily nutrition target")
    target_df = pd.DataFrame({
        "Macro": ["Protein", "Carbohydrates", "Fat"],
        "Grams": [targets["protein"], targets["carbs"], targets["fat"]]
    })
    fig = px.bar(target_df, x="Macro", y="Grams", title="Target Macros")
    st.plotly_chart(fig, use_container_width=True)

    if st.session_state.plan:
        flat = flatten_plan(st.session_state.plan)
        df = pd.DataFrame(flat)
        if not df.empty:
            totals = daily_totals(df)
            st.subheader("Current plan summary")
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Planned Calories", f"{totals['calories']:.0f}")
            d2.metric("Protein", f"{totals['protein']:.1f} g")
            d3.metric("Carbs", f"{totals['carbs']:.1f} g")
            d4.metric("Fat", f"{totals['fat']:.1f} g")
            chart_df = df.groupby("day", as_index=False)["calories"].sum()
            fig2 = px.line(chart_df, x="day", y="calories", markers=True, title="Calories by Day")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No weekly plan yet. Open Weekly Planner and generate one.")

with tabs[1]:
    st.subheader("Generate a 7-day meal plan")
    meals_per_day = st.slider("Meals per day", 3, 6, 4)
    seed = st.number_input("Planner seed", 1, 999999, 42)

    if st.button("🚀 Generate Weekly Plan", type="primary"):
        custom = get_custom_meals()
        st.session_state.plan = build_week_plan(
            targets=targets,
            meals_per_day=meals_per_day,
            dietary=dietary,
            allergies=allergies,
            min_protein=target_protein,
            custom_meals=custom,
            seed=int(seed),
        )
        save_plan(st.session_state.plan)
        st.success("Weekly meal plan generated and saved.")

    if st.session_state.plan:
        flat = flatten_plan(st.session_state.plan)
        df = pd.DataFrame(flat)
        for day in df["day"].drop_duplicates():
            st.markdown(f"### {day}")
            day_df = df[df["day"] == day].copy()
            show = day_df[["meal_type", "name", "calories", "protein", "carbs", "fat", "diet"]]
            st.dataframe(show, use_container_width=True, hide_index=True)
            totals = daily_totals(day_df)
            st.caption(
                f"Total: {totals['calories']:.0f} kcal · "
                f"{totals['protein']:.1f}g protein · "
                f"{totals['carbs']:.1f}g carbs · {totals['fat']:.1f}g fat"
            )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Current Plan"):
                save_plan(st.session_state.plan)
                st.success("Saved.")
        with col2:
            if st.button("🗑️ Clear Plan"):
                clear_plan()
                st.session_state.plan = None
                st.rerun()

with tabs[2]:
    st.subheader("Meal Library")
    from src.meals import MEALS
    custom = get_custom_meals()
    library = MEALS + custom

    q = st.text_input("Search meals", placeholder="e.g. chicken, oats, paneer...")
    max_cal = st.slider("Maximum calories", 50, 1200, 800)
    min_p = st.slider("Minimum protein (g)", 0, 100, 10)
    diets = st.multiselect("Diet tags", sorted(set(m["diet"] for m in library)))

    rows = []
    for m in library:
        if q and q.lower() not in (m["name"] + " " + " ".join(m["ingredients"])).lower():
            continue
        if m["calories"] > max_cal or m["protein"] < min_p:
            continue
        if diets and m["diet"] not in diets:
            continue
        rows.append(m)

    st.write(f"Showing **{len(rows)}** meals")
    if rows:
        view = pd.DataFrame(rows)[
            ["name", "meal_type", "diet", "calories", "protein", "carbs", "fat", "fiber"]
        ]
        st.dataframe(view, use_container_width=True, hide_index=True)

        for m in rows[:12]:
            with st.expander(f"{m['name']} — {m['calories']} kcal"):
                st.write("**Ingredients:** " + ", ".join(m["ingredients"]))
                st.write(
                    f"Protein: {m['protein']}g · Carbs: {m['carbs']}g · "
                    f"Fat: {m['fat']}g · Fiber: {m['fiber']}g"
                )
    else:
        st.warning("No meals match the current filters.")

with tabs[3]:
    st.subheader("Create a custom meal")
    with st.form("custom_meal"):
        name = st.text_input("Meal name")
        meal_type = st.selectbox("Meal type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        diet = st.selectbox("Diet", ["Vegetarian", "Vegan", "Non-Vegetarian", "High Protein"])
        ingredients = st.text_area("Ingredients (comma separated)")
        calories = st.number_input("Calories", 0.0, 3000.0, 400.0)
        protein = st.number_input("Protein (g)", 0.0, 300.0, 25.0)
        carbs = st.number_input("Carbohydrates (g)", 0.0, 500.0, 40.0)
        fat = st.number_input("Fat (g)", 0.0, 300.0, 12.0)
        fiber = st.number_input("Fiber (g)", 0.0, 100.0, 6.0)
        submitted = st.form_submit_button("Add Meal", type="primary")
        if submitted:
            if not name.strip():
                st.error("Meal name is required.")
            else:
                add_custom_meal({
                    "name": name.strip(),
                    "meal_type": meal_type,
                    "diet": diet,
                    "ingredients": [x.strip() for x in ingredients.split(",") if x.strip()],
                    "calories": calories,
                    "protein": protein,
                    "carbs": carbs,
                    "fat": fat,
                    "fiber": fiber,
                })
                st.success("Custom meal added.")
                st.rerun()

    custom = get_custom_meals()
    if custom:
        st.markdown("### Your custom meals")
        for m in custom:
            col1, col2 = st.columns([5, 1])
            col1.write(f"**{m['name']}** — {m['calories']:.0f} kcal · {m['protein']:.1f}g protein")
            if col2.button("Delete", key=f"delete_{m['id']}"):
                delete_custom_meal(m["id"])
                st.rerun()

with tabs[4]:
    st.subheader("Export your plan")
    if not st.session_state.plan:
        st.info("Generate a weekly plan first.")
    else:
        flat = flatten_plan(st.session_state.plan)
        df = pd.DataFrame(flat)
        csv_data = dataframe_to_csv(df)
        json_data = plan_to_json(st.session_state.plan)

        st.download_button(
            "⬇️ Download CSV",
            csv_data,
            file_name="nutrition_meal_plan.csv",
            mime="text/csv"
        )
        st.download_button(
            "⬇️ Download JSON",
            json_data,
            file_name="nutrition_meal_plan.json",
            mime="application/json"
        )

st.divider()
st.caption("Educational planning tool. Nutrition needs vary by person; consult a qualified healthcare professional for individualized medical or dietary advice.")
