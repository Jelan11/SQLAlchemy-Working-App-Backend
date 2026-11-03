from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise


def populate_database():
    with app.app_context():

        # Insert the starter exercises.
        starter_exercises = [
            {
                "name": "Pull-ups",
                "category": "Body weight exercise",
                "equipment_needed": False,
            },
            {
                "name": "Bicep Curls",
                "category": "Strength training",
                "equipment_needed": True,
            },
            {
                "name": "Running",
                "category": "Cardio",
                "equipment_needed": False,
            },
            {
                "name": "Push-ups",
                "category": "Body weight exercise",
                "equipment_needed": False,
            },
        ]

        for entry in starter_exercises:
            existing_exercise = Exercise.query.filter_by(
                name=entry["name"]
            ).first()

            if existing_exercise is None:
                db.session.add(Exercise(**entry))

        db.session.flush()

        # Set up a sample workout.
        sample_workout = Workout.query.filter_by(
            date=date.today(),
            notes="Sample workout from seed script",
        ).first()

        if sample_workout is None:
            sample_workout = Workout(
                date=date.today(),
                duration_minutes=30,
                notes="Sample workout from seed script",
            )

            db.session.add(sample_workout)
            db.session.flush()

        # Attach Push-ups to that workout.
        push_ups = Exercise.query.filter_by(
            name="Push-ups"
        ).first()

        current_link = WorkoutExercise.query.filter_by(
            workout_id=sample_workout.id,
            exercise_id=push_ups.id,
        ).first()

        if current_link is None:
            db.session.add(
                WorkoutExercise(
                    workout_id=sample_workout.id,
                    exercise_id=push_ups.id,
                    reps=10,
                    sets=3,
                )
            )

        db.session.commit()

        print("Seed data added successfully!")


if __name__ == "__main__":
    populate_database()