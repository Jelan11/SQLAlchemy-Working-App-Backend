from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from datetime import date

class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, validate=validate.Range(min=1))
    sets = fields.Int(allow_none=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(allow_none=True, validate=validate.Range(min=1))
    exercise = fields.Nested('ExerciseSchema', only=('id', 'name', 'category', 'equipment_needed'), dump_only=True)
    workout = fields.Nested('WorkoutSchema', only=('id', 'date', 'duration_minutes'), dump_only=True)
    
    @validates_schema
    def require_reps_or_duration(self,data, **kwargs):
        if data.get('reps') is None and data.get('duration_seconds') is None:
            raise ValidationError('Provide reps and/or duration_seconds.', 'reps')
    
    
class ExerciseSchema(Schema) : 
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=1,max= 100))
    category = fields.Str(required=True,validate=validate.Length(min=1,max= 50))
    equipment_needed = fields.Bool(load_default=False)

    workout_exercise =fields.List(
        fields.Nested(WorkoutExerciseSchema, only=('id', 'reps', 'sets', 'duration_seconds', 'exercise')),
        dump_only=True,
    )
    
    @validates('name')
    def validate_name(self,value):
        if not value.strip():
            raise ValidationError('name cannot be empty')
        
    @validates('category')
    def validate_category(self,value):
        if not value.strip():
            raise ValidationError('category cannot be empty')
        
        
class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True,validate=validate.Range(min=1,max=1440))
    notes =fields.Str = fields.Str(required =True, validate = validate.Length(max=100))
    
    workout_exercises = fields.List(
        fields.Nested(WorkoutExerciseSchema, only=('id', 'reps', 'sets', 'duration_seconds', 'exercise')),
        dump_only=True,
    )
    
    @validates ('date')
    def validate_date(self,value):
        if value.year < 2000:
            raise ValidationError ('date must start in the year 2000 or later')
    
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema (many=True,exclude=('workout_exercises',))
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True,exclude=('workout_exercises'),)
workout_exercise_schema = WorkoutExerciseSchema()