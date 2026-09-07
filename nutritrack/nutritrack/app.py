import os
import json
import hashlib
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get("NUTRITRACK_SECRET", "dev-only-change-this-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "athlete": 1.9,
}

ACTIVITY_LABELS = {
    "sedentary": "Sedentary (little to no exercise)",
    "light": "Lightly active (1-3 days/week)",
    "moderate": "Moderately active (3-5 days/week)",
    "active": "Active (6-7 days/week)",
    "athlete": "Athlete (very hard training)",
}

DIET_LABELS = {
    "bulking": "Bulking",
    "cutting": "Cutting",
    "maintenance": "Maintenance",
}

INTENSITY_MAP = {
    "bulking": {"intensity": "High", "sets": "4-5", "reps": "6-10", "rest": "2-3 min"},
    "cutting": {"intensity": "Moderate-High", "sets": "3-4", "reps": "12-15", "rest": "60-90 sec"},
    "maintenance": {"intensity": "Moderate", "sets": "3-4", "reps": "10-12", "rest": "90 sec"},
}


# ---------------------------------------------------------------------------
# User storage
# ---------------------------------------------------------------------------

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
    return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def hash_pw(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# ---------------------------------------------------------------------------
# Calculation logic
# ---------------------------------------------------------------------------

def calc_bmr(age, gender, height_cm, weight_kg):
    """Mifflin-St Jeor equation."""
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    if gender == "male":
        return base + 5
    return base - 161  # female / other uses the female constant as a baseline


def calc_tdee(bmr, activity_level):
    return bmr * ACTIVITY_MULTIPLIERS[activity_level]


def build_diet_plan(age, gender, height_cm, weight_kg, activity_level, diet_goal):
    bmr = calc_bmr(age, gender, height_cm, weight_kg)
    tdee = calc_tdee(bmr, activity_level)

    calorie_targets = {
        "bulking": tdee + 500,
        "cutting": tdee - 500,
        "maintenance": tdee,
    }
    target_calories = calorie_targets[diet_goal]

    protein_g = weight_kg * 2.2
    fat_g = weight_kg * 0.5
    fiber_g = target_calories * 0.014
    # Remaining calories after protein + fat go to carbohydrate (4 kcal/g protein & carb, 9 kcal/g fat)
    remaining_calories = max(target_calories - (protein_g * 4) - (fat_g * 9), 0)
    carbs_g = remaining_calories / 4

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "calories": round(target_calories),
        "protein": round(protein_g, 1),
        "fat": round(fat_g, 1),
        "fiber": round(fiber_g, 1),
        "carbs": round(carbs_g, 1),
    }


def build_workout_plan(workout_type, diet_goal):
    profile = INTENSITY_MAP[diet_goal]
    sets, reps = profile["sets"], profile["reps"]

    if workout_type == "gym":
        days = {
            "Day 1 — Chest & Triceps": [
                ("Barbell Bench Press", sets, reps),
                ("Incline Dumbbell Press", sets, reps),
                ("Cable Flyes", "3", "12-15"),
                ("Weighted Dips", sets, reps),
                ("Tricep Rope Pushdown", "3", "12-15"),
                ("Overhead Tricep Extension", "3", "12-15"),
            ],
            "Day 2 — Back & Biceps": [
                ("Deadlift", sets, "5-8" if diet_goal == "bulking" else "8-10"),
                ("Pull-ups / Lat Pulldown", sets, reps),
                ("Barbell Rows", sets, reps),
                ("Seated Cable Rows", "3", "12-15"),
                ("Barbell Bicep Curl", sets, reps),
                ("Hammer Curls", "3", "12-15"),
                ("Face Pulls", "3", "15-20"),
            ],
            "Day 3 — Legs": [
                ("Barbell Squat", sets, "6-10"),
                ("Romanian Deadlift", sets, reps),
                ("Leg Press", sets, reps),
                ("Leg Curl", "3", "12-15"),
                ("Leg Extension", "3", "12-15"),
                ("Calf Raises", "4", "15-20"),
                ("Walking Lunges", "3", "12 each leg"),
            ],
            "Day 4 — Shoulders & Abs": [
                ("Military Press", sets, reps),
                ("Lateral Raises", "4", "12-15"),
                ("Front Raises", "3", "12-15"),
                ("Rear Delt Flyes", "3", "15-20"),
                ("Shrugs", "3", "12-15"),
                ("Hanging Leg Raises", "3", "15-20"),
                ("Cable Crunches", "3", "15-20"),
                ("Plank", "3", "60 sec"),
            ],
            "Day 5 — Full Body / Power": [
                ("Clean and Press", "3-4", "6-8"),
                ("Front Squat", sets, reps),
                ("Incline Bench Press", sets, reps),
                ("Weighted Pull-ups", sets, reps),
                ("Dumbbell Lunges", "3", "10 each"),
                ("Farmer's Walk", "3", "40m"),
                ("Battle Ropes", "3", "30 sec"),
            ],
        }
    else:
        days = {
            "Day 1 — Chest & Triceps": [
                ("Push-ups (Regular / Decline / Diamond)", sets, reps),
                ("Pike Push-ups", sets, reps),
                ("Wide Push-ups", "3", "12-15"),
                ("Tricep Dips (Chair / Bench)", sets, reps),
                ("Diamond Push-ups", "3", "10-12"),
                ("Close-grip Push-ups", "3", "12-15"),
            ],
            "Day 2 — Back & Biceps": [
                ("Pull-ups / Chin-ups (if bar available)", sets, reps),
                ("Inverted Rows (Table / Bar)", sets, reps),
                ("Superman Pulls", "3", "15-20"),
                ("Towel Bicep Curls", sets, reps),
                ("Resistance Band Rows", sets, reps),
                ("Doorway Curls", "3", "12-15"),
            ],
            "Day 3 — Legs": [
                ("Bulgarian Split Squats", sets, "12 each"),
                ("Jump Squats", "3-4", "10-15"),
                ("Single-leg Deadlift", sets, "12 each"),
                ("Walking Lunges", "3", "15 each"),
                ("Wall Sit", "3", "45-60 sec"),
                ("Calf Raises (Single leg)", "4", "20 each"),
                ("Glute Bridges", "3", "15-20"),
            ],
            "Day 4 — Shoulders & Abs": [
                ("Pike Push-ups", sets, reps),
                ("Handstand Hold / Push-ups", "3", "Max time/reps"),
                ("Lateral Raise (Water bottles / bands)", "4", "12-15"),
                ("Front Raise (Books / bands)", "3", "12-15"),
                ("Plank to Pike", "3", "12-15"),
                ("Bicycle Crunches", "3", "20 each side"),
                ("Leg Raises", "3", "15-20"),
                ("Mountain Climbers", "3", "30 sec"),
            ],
            "Day 5 — Full Body / Cardio": [
                ("Burpees", "4", "10-15"),
                ("Jump Squats", sets, reps),
                ("Push-up to T", "3", "10 each side"),
                ("High Knees", "3", "45 sec"),
                ("Plank Jacks", "3", "30 sec"),
                ("Jumping Lunges", "3", "12 each"),
                ("Spider-man Push-ups", "3", "10 each side"),
                ("Shadow Boxing", "3", "60 sec"),
            ],
        }

    recovery_notes = {
        "bulking": [
            "Focus on progressive overload",
            "Prioritize compound movements",
            "Rest 2-3 minutes between heavy sets",
            "Sleep 7-9 hours for muscle recovery",
        ],
        "cutting": [
            "Maintain strength, don't chase PRs",
            "Add 20-30 min cardio 3x/week",
            "Shorter rest periods to keep heart rate up",
            "Prioritize protein to preserve muscle",
        ],
        "maintenance": [
            "Balance strength and endurance work",
            "Focus on consistent form",
            "Add 2-3 cardio sessions per week",
            "Maintain current fitness levels",
        ],
    }

    return {
        "intensity": profile["intensity"],
        "rest": profile["rest"],
        "days": days,
        "notes": recovery_notes[diet_goal],
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("profile"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        users = load_users()
        if not username:
            flash("Username cannot be empty.", "error")
        elif username in users:
            flash("That username is already taken.", "error")
        elif len(password) < 4:
            flash("Password must be at least 4 characters.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            users[username] = {"password": hash_pw(password)}
            save_users(users)
            flash("Account created. You can log in now.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        users = load_users()

        if username in users and users[username]["password"] == hash_pw(password):
            session["username"] = username
            return redirect(url_for("profile"))
        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        try:
            age = int(request.form["age"])
            gender = request.form["gender"]
            height_cm = float(request.form["height"])
            weight_kg = float(request.form["weight"])
            activity_level = request.form["activity"]
            diet_goal = request.form["diet"]
            workout_type = request.form["workout"]

            if age <= 0 or height_cm <= 0 or weight_kg <= 0:
                raise ValueError("Values must be positive.")
            if activity_level not in ACTIVITY_MULTIPLIERS:
                raise ValueError("Invalid activity level.")
            if diet_goal not in DIET_LABELS:
                raise ValueError("Invalid diet goal.")
            if workout_type not in ("gym", "home"):
                raise ValueError("Invalid workout type.")
        except (KeyError, ValueError):
            flash("Please fill in every field with a valid value.", "error")
            return render_template("profile.html")

        diet = build_diet_plan(age, gender, height_cm, weight_kg, activity_level, diet_goal)
        workout = build_workout_plan(workout_type, diet_goal)

        session["last_result"] = {
            "inputs": {
                "age": age,
                "gender": gender.capitalize(),
                "height": height_cm,
                "weight": weight_kg,
                "activity_label": ACTIVITY_LABELS[activity_level],
                "diet_label": DIET_LABELS[diet_goal],
                "workout_type": workout_type.capitalize(),
            },
            "diet": diet,
            "workout": workout,
        }
        return redirect(url_for("results"))

    return render_template("profile.html")


@app.route("/results")
@login_required
def results():
    result = session.get("last_result")
    if not result:
        return redirect(url_for("profile"))
    return render_template("results.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
