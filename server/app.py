import os

from flask import Flask, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import *
from schemas import (
    workout_schema, workouts_schema,
    exercise_schema, exercises_schema,
    workout_exercise_schema,
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


def error_response(message, status_code, details=None):
    payload = {'error': message}
    if details:
        payload['details'] = details
    return make_response(payload, status_code)


def find_by_id(model, record_id):
    return db.session.get(model, record_id)


# Exception handlers

@app.errorhandler(ValidationError)
def on_schema_validation_error(err):
    return error_response('Request data failed validation', 422, err.messages)


@app.errorhandler(ValueError)
def on_model_value_error(err):
    db.session.rollback()
    return error_response(str(err), 422)


@app.errorhandler(IntegrityError)
def on_integrity_error(err):
    db.session.rollback()
    return error_response('A database constraint was violated (duplicate or invalid data).', 409)


@app.errorhandler(404)
def on_not_found(err):
    return error_response('The requested resource could not be found', 404)


# Endpoints

@app.route('/')
def home():
    return make_response({'message': 'Workout API'}, 200)


@app.route('/workouts', methods=['GET'])
def list_workouts():
    all_workouts = Workout.query.order_by(Workout.date.desc()).all()
    return make_response(workouts_schema.dump(all_workouts), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def show_workout(id):
    workout = find_by_id(Workout, id)
    if not workout:
        return error_response(f'No workout found with id {id}', 404)
    return make_response(workout_schema.dump(workout), 200)


@app.route('/workouts', methods=['POST'])
def add_workout():
    payload = workout_schema.load(request.get_json(silent=True) or {})
    new_workout = Workout(**payload) # type:ignore
    db.session.add(new_workout)
    db.session.commit()
    return make_response(workout_schema.dump(new_workout), 201)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def remove_workout(id):
    workout = find_by_id(Workout, id)
    if not workout:
        return error_response(f'No workout found with id {id}', 404)
    db.session.delete(workout)  # also removes related WorkoutExercises
    db.session.commit()
    return make_response('', 204)


@app.route('/exercises', methods=['GET'])
def list_exercises():
    all_exercises = Exercise.query.order_by(Exercise.name).all()
    return make_response(exercises_schema.dump(all_exercises), 200)


@app.route('/exercises/<int:id>', methods=['GET'])
def show_exercise(id):
    exercise = find_by_id(Exercise, id)
    if not exercise:
        return error_response(f'No exercise found with id {id}', 404)
    return make_response(exercise_schema.dump(exercise), 200)


@app.route('/exercises', methods=['POST'])
def add_exercise():
    payload = exercise_schema.load(request.get_json(silent=True) or {})
    new_exercise = Exercise(**payload) # type:ignore
    db.session.add(new_exercise)
    db.session.commit()
    return make_response(exercise_schema.dump(new_exercise), 201)


@app.route('/exercises/<int:id>', methods=['DELETE'])
def remove_exercise(id):
    exercise = find_by_id(Exercise, id)
    if not exercise:
        return error_response(f'No exercise found with id {id}', 404)
    db.session.delete(exercise)  # also removes related WorkoutExercises
    db.session.commit()
    return make_response('', 204)


@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def attach_exercise_to_workout(workout_id, exercise_id):
    workout = find_by_id(Workout, workout_id)
    if not workout:
        return error_response(f'No workout found with id {workout_id}', 404)
    exercise = find_by_id(Exercise, exercise_id)
    if not exercise:
        return error_response(f'No exercise found with id {exercise_id}', 404)

    payload = workout_exercise_schema.load(request.get_json(silent=True) or {})
    new_link = WorkoutExercise(workout=workout, exercise=exercise, **payload) # type:ignore
    db.session.add(new_link)
    db.session.commit()
    return make_response(workout_exercise_schema.dump(new_link), 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)