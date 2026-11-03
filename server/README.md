# Workout Tracker API

A Flask REST API for personal trainers to track workouts and the exercises performed in them. Exercises are reusable across workouts, and each workout–exercise link records reps, sets, and/or duration.

Built with Flask, Flask-SQLAlchemy, Flask-Migrate, and Marshmallow.

## Data Model

- **Exercise**: `name` (unique), `category`, `equipment_needed`
- **Workout**: `date`, `duration_minutes`, `notes`
- **WorkoutExercise** (join table): `workout_id`, `exercise_id`, `reps`, `sets`, `duration_seconds`

A Workout has many Exercises through WorkoutExercises, and vice versa. Deleting a Workout or Exercise also deletes its WorkoutExercises.

## Validations

| Level | Rules |
|-------|-------|
| Table constraints | Unique exercise name; non-blank name/category; `duration_minutes > 0`; reps/sets/duration_seconds > 0; each WorkoutExercise needs `reps` or `duration_seconds`; an exercise can be added to a workout only once |
| Model (`@validates`) | Non-blank exercise name/category; boolean `equipment_needed`; positive `duration_minutes`; valid `date`; positive reps/sets/duration_seconds |
| Schema (Marshmallow) | Required fields and types; length limits; `duration_minutes` 1–1440; date must be 2000 or later; reps/sets/duration >= 1; `reps` or `duration_seconds` required |

## Installation

```bash
git clone <your-repo-url>
cd workout-api
pipenv install
pipenv shell
cd server
export FLASK_APP=app.py
flask db upgrade head      
python seed.py             
```

To start from scratch instead of using the included migration: delete `server/migrations` and `server/instance`, then run `flask db init`, `flask db migrate -m 'message'`, and `flask db upgrade head`.

## Running

```bash
cd server
flask run -p 5555
# or
python app.py
```

The API is served at `http://localhost:5555`.

## Tests

```bash
cd server
pytest
```

## Endpoints

| Method | Path | Description | Success |
|--------|------|-------------|---------|
| GET | `/workouts` | List all workouts | 200 |
| GET | `/workouts/<id>` | Show one workout with its exercises, including reps/sets/duration | 200 |
| POST | `/workouts` | Create a workout | 201 |
| DELETE | `/workouts/<id>` | Delete a workout and its WorkoutExercises | 204 |
| GET | `/exercises` | List all exercises | 200 |
| GET | `/exercises/<id>` | Show one exercise with the workouts it appears in | 200 |
| POST | `/exercises` | Create an exercise | 201 |
| DELETE | `/exercises/<id>` | Delete an exercise and its WorkoutExercises | 204 |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout with reps/sets/duration | 201 |

### Request examples

```bash
curl -X POST localhost:5555/workouts -H 'Content-Type: application/json' \
  -d '{"date": "2025-02-01", "duration_minutes": 45, "notes": "Leg day"}'

curl -X POST localhost:5555/exercises -H 'Content-Type: application/json' \
  -d '{"name": "Lunge", "category": "Strength", "equipment_needed": false}'

curl -X POST localhost:5555/workouts/1/exercises/1/workout_exercises \
  -H 'Content-Type: application/json' -d '{"reps": 10, "sets": 3}'
```

### Errors

- `404`: resource not found
- `409`: database constraint violated (e.g. duplicate exercise name, or exercise already in the workout)
- `422`: validation failed; response is `{"error": ..., "details": {...}}`# -Flask-SQLAlchemy-Workout-Application-Backend