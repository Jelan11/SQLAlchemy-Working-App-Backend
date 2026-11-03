from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Exercise(db.Model):
    __tablename__ = 'exercises'

    __table_args__ = (
        db.CheckConstraint('length(trim(name)) > 0', name='ck_exercise_name_not_blank'),
        db.CheckConstraint('length(trim(category)) > 0', name='ck_exercise_category_not_blank'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan'
    )

    workouts = association_proxy('workout_exercises', 'workout')

    @validates('name', 'category')
    def check_text_field(self, field, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{field} cannot be empty or blank.')
        return value.strip()

    @validates('equipment_needed')
    def check_equipment_flag(self, field, value):
        if not isinstance(value, bool):
            raise ValueError('equipment_needed must be either true or false.')
        return value

    def __repr__(self):
        return f'<Exercise {self.id}: {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'
    __table_args__ = (
        db.CheckConstraint('duration_minutes > 0', name='ck_workout_duration_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='workout', cascade='all, delete-orphan'
    )

    exercises = association_proxy('workout_exercises', 'exercise')

    @validates('duration_minutes')
    def check_duration(self, field, value):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError('duration_minutes must be an integer greater than zero.')
        return value

    @validates('date')
    def check_date(self, field, value):
        # Imported locally so the top of the module stays uncluttered.
        from datetime import date as date_type
        if not isinstance(value, date_type):
            raise ValueError('date must be a real calendar date.')
        return value

    def __repr__(self):
        return f'<Workout {self.id}: {self.date}>'


class WorkoutExercise(db.Model):
    """Association table linking Workout and Exercise, holding the performance details."""
    __tablename__ = 'workout_exercises'

    __table_args__ = (
        db.UniqueConstraint('workout_id', 'exercise_id', name='uq_workout_exercise'),
        db.CheckConstraint(
            'reps IS NOT NULL OR duration_seconds IS NOT NULL',
            name='ck_workout_exercise_has_metric',
        ),
        db.CheckConstraint('reps IS NULL OR reps > 0', name='ck_reps_positive'),
        db.CheckConstraint('sets IS NULL OR sets > 0', name='ck_sets_positive'),
        db.CheckConstraint(
            'duration_seconds IS NULL OR duration_seconds > 0',
            name='ck_duration_seconds_positive',
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # Each WorkoutExercise points back to one Workout and one Exercise.
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    @validates('reps', 'sets', 'duration_seconds')
    def check_positive_integer(self, field, value):
        if value is None:
            return value
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f'{field} must be an integer greater than zero.')
        return value

    def __repr__(self):
        return f'<WorkoutExercise workout={self.workout_id} exercise={self.exercise_id}>'