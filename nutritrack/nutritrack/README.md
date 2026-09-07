# NutriTrack

A small Flask app version of the NutriTrack script: user accounts, a
calorie/macro calculator, and a 5-day workout split — dark theme only.

## Run it

```bash
pip install flask
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## How it's organized

```
nutritrack/
├── app.py                 # routes, auth, and all calculations
├── users.json              # created automatically on first registration
├── templates/               # HTML (Jinja2)
└── static/css/style.css      # dark, flat, nutrition-label-inspired theme
```

## Accounts

- Passwords are hashed with SHA-256 before being written to `users.json` —
  the plain password is never stored.
- `users.json` is created the first time someone registers, in the same
  folder as `app.py`.

## Calculations

- **BMR** — Mifflin-St Jeor equation (uses the male/female constant based
  on the gender selected at registration time... actually per plan, not
  account).
- **TDEE** — BMR × an activity multiplier (sedentary 1.2 → athlete 1.9).
- **Calorie target** — TDEE ± 500 kcal for bulking/cutting, TDEE as-is for
  maintenance.
- **Macros** — protein and fat are set directly from body weight, fiber
  scales with the calorie target, and carbs fill in whatever calories are
  left after protein and fat are accounted for (4 kcal/g for protein and
  carbs, 9 kcal/g for fat) — so the four numbers always add back up to the
  daily calorie target.
- **Workout plan** — a 5-day gym or home split, with set/rep ranges and
  rest periods tuned to the diet goal (heavier & slower for bulking,
  lighter & faster for cutting).

## Notes

- This is a learning/personal-use app, not hardened for production: the
  dev server (`app.run(debug=True)`) is fine locally but shouldn't be
  exposed to the internet as-is, and `app.secret_key` should be set via
  the `NUTRITRACK_SECRET` environment variable rather than the default.
