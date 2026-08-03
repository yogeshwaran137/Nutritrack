from datetime import *
import os
import json
import hashlib
import getpass

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)

def hash_pw(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user():
    users = load_users()
    print("\n--- Register ---")
    username = input("Choose a username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return False
    if username in users:
        print("Username already exists.")
        return False
    pw = getpass.getpass("Choose a password: ")
    pw2 = getpass.getpass("Confirm password: ")
    if pw != pw2:
        print("Passwords do not match.")
        return False
    users[username] = hash_pw(pw)
    save_users(users)
    print("Registration successful. You can now log in.\n")
    return True

def login_prompt():
    users = load_users()
    if not users:
        print("No users found. Please register an account first.")
        if not register_user():
            print("Registration failed. Exiting.")
            exit(1)
        users = load_users()

    attempts = 3
    for _ in range(attempts):
        print("\n--- Login ---")
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        if username in users and users[username] == hash_pw(password):
            print("Login successful.\n")
            return username
        print("Invalid credentials. Try again.")
    print("Too many failed attempts. Exiting.")
    exit(1)

class healthcare:
    def __init__(self,age,gender,height,weight,act_lvl):
        self.age = age
        self.gender = gender
        self.height = height
        self.weight = weight
        self.act_lvl = act_lvl
    
    def __del__(self):
         pass
        
    def BMR(self):
        if self.gender.lower() == "male":
            #(10 x weight in kg) + (6.25 x height in cm) - (5 x age in years) + 5 for male
           return ((10*self.weight) + (6.25*self.height) - (5*self.age) + 5)
        
        elif self.gender.lower() == "female":
            # it is (10 x weight in kg) + (6.25 x height in cm) - (5 x age in years) - 161 for female
            return (10*self.weight) + (6.25*self.height) - (5*self.age) - 161
        
   
    def TDEE(self):
            calories = self.BMR()
            if self.act_lvl.lower() == "light":
                #Lightly Active: BMR x 1.375
                 return float(calories) * 1.375
            
            elif self.act_lvl.lower() == "sedentral":
                #sedentral active: BMR x 1.2
                 return float(calories) * 1.2
            
            elif self.act_lvl.lower() == "moderate":
                #moderately active: BMR x 1.55
                 return float(calories) * 1.55
            
            elif self.act_lvl.lower() == "active":
                 #Active: BMR x 1.725
                 return float(calories) * 1.725
            
            elif self.act_lvl.lower() == "athlete":
                 return float(calories) * 1.9
            
            else:
                 print("Invalid input!!")

# main program
print("Welcome to NUTRITRACK!!")
while True:
    choice = input("Do you want to (L)ogin or (R)egister? [L/R]: ").strip().lower()
    if choice == 'r':
        register_user()
    elif choice == 'l':
        current_user = login_prompt()
        break
    else:
        print("Enter 'L' to login or 'R' to register.")

age = int(input("Enter your age (in years): "))
gender = input("Enter your gender: ")
weight = float(input("Enter your weight (in Kg): "))
height = float(input("Enter your height(in cm): "))
print()
print("--------------------------------")
act_lvl = input("       Activity level\n"
                "--------------------------------\n"
                "Light\n"
                "Moderate\n"
                "Active\n"
                "Athlete(Extremely active)\n"
                "--------------------------------\n"
                "Enter: ")
print()

data = healthcare(age,gender,height,weight,act_lvl)
print("------------------------------")
diet_type = input("     Type of diet\n" 
                  "------------------------------\n"
                  "Bulking\n"
                  "Cutting\n"
                  "Maintainance\n"
                  "------------------------------\n"
                  "Enter : ").lower()

protien = weight * (2.2)
print()
calories = data.TDEE()
fiber = calories * 0.014
fat = weight * 0.5

b_cal = calories + 500
c_cal = calories - 500
m_cal = calories 
type = {
     "bulking":b_cal,
     "cutting":c_cal,
     "maintainance":m_cal
}
for keys,values in type.items():
     if keys == diet_type.lower() :
          print("--------------------------------------------------------")
          print("                  DIET SUGGESTION")
          print("--------------------------------------------------------\n")
          print("Your daily Calorie intake: ",round(values,2))
          print("Your daily Protien intake should be: ",round(protien,2) ,"grams")
          print("Your daily Fat intake should be: ",round(fat,2),"grams")
          print("Your daily Fiber intake should be: ",round(fiber,2) ,"grams")
          print("---------------------------------------------------------\n")
          break

def workout_plan(workout_type, diet_type):
    """Print workout plan based on workout type (gym/home) and diet goal"""
    
    # Determine intensity based on diet type
    intensity_map = {
        "bulking": ("High", "4-5", "6-10", "2-3 min"),
        "cutting": ("Moderate-High", "3-4", "12-15", "60-90 sec"),
        "maintainance": ("Moderate", "3-4", "10-12", "90 sec")
    }
    
    intensity, sets, reps, rest = intensity_map.get(diet_type.lower(), ("Moderate", "3-4", "10-12", "90 sec"))
    
    print("\n" + "="*70)
    print(f"  {workout_type.upper()} WORKOUT PLAN - 5 DAY SPLIT ({diet_type.upper()})")
    print("="*70)
    print(f"\nIntensity Level: {intensity}")
    print(f"Rest Between Sets: {rest}")
    print(f"Goal: {diet_type.capitalize()}\n")
    
    if workout_type.lower() == "gym":
        gym_plan = {
            "Day 1 - CHEST & TRICEPS": [
                ("Barbell Bench Press", sets, reps),
                ("Incline Dumbbell Press", sets, reps),
                ("Cable Flyes", "3", "12-15"),
                ("Dips (Weighted if possible)", sets, reps),
                ("Tricep Rope Pushdown", "3", "12-15"),
                ("Overhead Tricep Extension", "3", "12-15")
            ],
            "Day 2 - BACK & BICEPS": [
                ("Deadlift", sets, "5-8" if diet_type.lower() == "bulking" else "8-10"),
                ("Pull-ups/Lat Pulldown", sets, reps),
                ("Barbell Rows", sets, reps),
                ("Seated Cable Rows", "3", "12-15"),
                ("Barbell Bicep Curl", sets, reps),
                ("Hammer Curls", "3", "12-15"),
                ("Face Pulls", "3", "15-20")
            ],
            "Day 3 - LEGS": [
                ("Barbell Squat", sets, "6-10"),
                ("Romanian Deadlift", sets, reps),
                ("Leg Press", sets, reps),
                ("Leg Curl", "3", "12-15"),
                ("Leg Extension", "3", "12-15"),
                ("Calf Raises", "4", "15-20"),
                ("Walking Lunges", "3", "12 each leg")
            ],
            "Day 4 - SHOULDERS & ABS": [
                ("Military Press", sets, reps),
                ("Lateral Raises", "4", "12-15"),
                ("Front Raises", "3", "12-15"),
                ("Rear Delt Flyes", "3", "15-20"),
                ("Shrugs", "3", "12-15"),
                ("Hanging Leg Raises", "3", "15-20"),
                ("Cable Crunches", "3", "15-20"),
                ("Plank", "3", "60 sec")
            ],
            "Day 5 - FULL BODY/POWER": [
                ("Clean and Press", "3-4", "6-8"),
                ("Front Squat", sets, reps),
                ("Incline Bench Press", sets, reps),
                ("Weighted Pull-ups", sets, reps),
                ("Dumbbell Lunges", "3", "10 each"),
                ("Farmers Walk", "3", "40m"),
                ("Battle Ropes", "3", "30 sec")
            ]
        }
        
        for day, exercises in gym_plan.items():
            print(f"\n{day}")
            print("-" * 70)
            for i, (exercise, ex_sets, ex_reps) in enumerate(exercises, 1):
                print(f"  {i}. {exercise:<35} {ex_sets} sets x {ex_reps} reps")
    
    elif workout_type.lower() == "home":
        home_plan = {
            "Day 1 - CHEST & TRICEPS": [
                ("Push-ups (Regular/Decline/Diamond)", sets, reps),
                ("Pike Push-ups", sets, reps),
                ("Wide Push-ups", "3", "12-15"),
                ("Tricep Dips (Chair/Bench)", sets, reps),
                ("Diamond Push-ups", "3", "10-12"),
                ("Close-grip Push-ups", "3", "12-15")
            ],
            "Day 2 - BACK & BICEPS": [
                ("Pull-ups/Chin-ups (if bar available)", sets, reps),
                ("Inverted Rows (Table/Bar)", sets, reps),
                ("Superman Pulls", "3", "15-20"),
                ("Towel Bicep Curls", sets, reps),
                ("Resistance Band Rows", sets, reps),
                ("Doorway Curls", "3", "12-15")
            ],
            "Day 3 - LEGS": [
                ("Bulgarian Split Squats", sets, "12 each"),
                ("Jump Squats", "3-4", "10-15"),
                ("Single-leg Deadlift", sets, "12 each"),
                ("Walking Lunges", "3", "15 each"),
                ("Wall Sit", "3", "45-60 sec"),
                ("Calf Raises (Single leg)", "4", "20 each"),
                ("Glute Bridges", "3", "15-20")
            ],
            "Day 4 - SHOULDERS & ABS": [
                ("Pike Push-ups", sets, reps),
                ("Handstand Hold/Push-ups", "3", "Max time/reps"),
                ("Lateral Raise (Water bottles/bands)", "4", "12-15"),
                ("Front Raise (Books/bands)", "3", "12-15"),
                ("Plank to Pike", "3", "12-15"),
                ("Bicycle Crunches", "3", "20 each side"),
                ("Leg Raises", "3", "15-20"),
                ("Mountain Climbers", "3", "30 sec")
            ],
            "Day 5 - FULL BODY/CARDIO": [
                ("Burpees", "4", "10-15"),
                ("Jump Squats", sets, reps),
                ("Push-up to T", "3", "10 each side"),
                ("High Knees", "3", "45 sec"),
                ("Plank Jacks", "3", "30 sec"),
                ("Jumping Lunges", "3", "12 each"),
                ("Spider-man Push-ups", "3", "10 each side"),
                ("Shadow Boxing", "3", "60 sec")
            ]
        }
        
        for day, exercises in home_plan.items():
            print(f"\n{day}")
            print("-" * 70)
            for i, (exercise, ex_sets, ex_reps) in enumerate(exercises, 1):
                print(f"  {i}. {exercise:<40} {ex_sets} sets x {ex_reps} reps")
    
    print("\n" + "="*70)
    print("RECOVERY NOTES:")
    print("-" * 70)
    if diet_type.lower() == "bulking":
        print("• Focus on progressive overload")
        print("• Prioritize compound movements")
        print("• Rest 2-3 minutes between heavy sets")
        print("• Sleep 7-9 hours for muscle recovery")
    elif diet_type.lower() == "cutting":
        print("• Maintain strength, don't chase PRs")
        print("• Consider adding 20-30 min cardio 3x/week")
        print("• Shorter rest periods to maintain heart rate")
        print("• Prioritize protein to preserve muscle")
    else:
        print("• Balance between strength and endurance")
        print("• Focus on consistent form")
        print("• Add 2-3 cardio sessions per week")
        print("• Maintain current fitness levels")
    print("="*70 + "\n")

wp = input("enter workout type(Gym/Home):").lower()
workout_plan(wp,diet_type)















