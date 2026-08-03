# Nutritrack
A Python-based health and fitness planner that calculates BMR, TDEE, nutrition requirements, and generates personalized gym or home workout plans

# NutriTrack

## Overview

NutriTrack is a Python-based health and fitness application that provides personalized nutrition and workout recommendations based on user information. The application calculates daily calorie requirements and generates workout plans according to the user's fitness goals.

## Features

- User registration and login
- Secure password storage using SHA-256 hashing
- Basal Metabolic Rate (BMR) calculation
- Total Daily Energy Expenditure (TDEE) calculation
- Diet recommendations for:
  - Bulking
  - Cutting
  - Maintenance
- Daily calorie, protein, fat, and fiber recommendations
- Personalized 5-day workout plans
- Gym and home workout options
- User data stored using JSON

## Technologies Used

- Python
- Object-Oriented Programming
- JSON
- hashlib
- getpass

## Project Structure

```
NutriTrack/
│
├── health.py
├── users.json
└── README.md
```


## Usage

1. Register a new account.
2. Log in using your credentials.
3. Enter your age, gender, height, weight, and activity level.
4. Select your fitness goal.
5. Choose either a gym or home workout plan.
6. View your personalized nutrition and workout recommendations.

## Future Improvements

- Graphical user interface
- SQLite database integration
- BMI calculator
- Progress tracking
- PDF report generation
- Meal planning
- Web application deployment

## License

This project is licensed under the MIT License.

