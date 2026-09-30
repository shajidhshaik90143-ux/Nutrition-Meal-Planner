import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "nutrition_planner.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS custom_meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                diet TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                carbs REAL NOT NULL,
                fat REAL NOT NULL,
                fiber REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS saved_plan (
                id INTEGER PRIMARY KEY CHECK (id=1),
                plan_json TEXT NOT NULL
            )
        """)
        conn.commit()

def add_custom_meal(meal):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO custom_meals
            (name, meal_type, diet, ingredients, calories, protein, carbs, fat, fiber)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            meal["name"], meal["meal_type"], meal["diet"],
            json.dumps(meal["ingredients"]), meal["calories"], meal["protein"],
            meal["carbs"], meal["fat"], meal["fiber"]
        ))
        conn.commit()

def get_custom_meals():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM custom_meals ORDER BY id DESC").fetchall()
    meals = []
    for r in rows:
        d = dict(r)
        d["ingredients"] = json.loads(d["ingredients"])
        meals.append(d)
    return meals

def delete_custom_meal(meal_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM custom_meals WHERE id=?", (meal_id,))
        conn.commit()

def save_plan(plan):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO saved_plan (id, plan_json) VALUES (1, ?)",
            (json.dumps(plan),)
        )
        conn.commit()

def load_plan():
    with get_connection() as conn:
        row = conn.execute("SELECT plan_json FROM saved_plan WHERE id=1").fetchone()
    return json.loads(row["plan_json"]) if row else None

def clear_plan():
    with get_connection() as conn:
        conn.execute("DELETE FROM saved_plan WHERE id=1")
        conn.commit()
