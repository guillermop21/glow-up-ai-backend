from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Información personal
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    height = db.Column(db.Float)  # en cm
    weight = db.Column(db.Float)  # en kg
    
    # Objetivos y preferencias
    fitness_goal = db.Column(db.String(50))  # weight_loss, muscle_gain, endurance, strength
    activity_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    dietary_restrictions = db.Column(db.String(100))
    
    # Suscripción
    subscription_type = db.Column(db.String(20), default='basic')  # basic, premium, pro
    subscription_expires = db.Column(db.DateTime)
    
    # Metadatos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relaciones
    workout_plans = db.relationship('WorkoutPlan', backref='user', lazy=True, cascade='all, delete-orphan')
    nutrition_plans = db.relationship('NutritionPlan', backref='user', lazy=True, cascade='all, delete-orphan')
    progress_entries = db.relationship('ProgressEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Establece la contraseña hasheada"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convierte el usuario a diccionario"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'fitness_goal': self.fitness_goal,
            'activity_level': self.activity_level,
            'dietary_restrictions': self.dietary_restrictions,
            'subscription_type': self.subscription_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def update_from_dict(self, data):
        """Actualiza el usuario desde un diccionario"""
        allowed_fields = [
            'name', 'age', 'gender', 'height', 'weight',
            'fitness_goal', 'activity_level', 'dietary_restrictions'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(self, field, data[field])
        
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<User {self.email}>'


class WorkoutPlan(db.Model):
    __tablename__ = 'workout_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_weeks = db.Column(db.Integer, default=4)
    workouts_per_week = db.Column(db.Integer, default=3)
    difficulty = db.Column(db.String(20))  # beginner, intermediate, advanced
    
    # Plan generado por IA
    plan_data = db.Column(db.Text)  # JSON con los entrenamientos
    
    # Estado
    status = db.Column(db.String(20), default='active')  # active, completed, paused
    progress = db.Column(db.Float, default=0.0)  # porcentaje de completado
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_plan_data(self):
        """Obtiene los datos del plan como diccionario"""
        if self.plan_data:
            return json.loads(self.plan_data)
        return {}
    
    def set_plan_data(self, data):
        """Establece los datos del plan desde un diccionario"""
        self.plan_data = json.dumps(data)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'duration_weeks': self.duration_weeks,
            'workouts_per_week': self.workouts_per_week,
            'difficulty': self.difficulty,
            'status': self.status,
            'progress': self.progress,
            'plan_data': self.get_plan_data(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class NutritionPlan(db.Model):
    __tablename__ = 'nutrition_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    daily_calories = db.Column(db.Integer)
    duration_weeks = db.Column(db.Integer, default=4)
    
    # Macronutrientes (porcentajes)
    protein_percentage = db.Column(db.Float)
    carbs_percentage = db.Column(db.Float)
    fats_percentage = db.Column(db.Float)
    
    # Plan generado por IA
    plan_data = db.Column(db.Text)  # JSON con las comidas
    
    # Estado
    status = db.Column(db.String(20), default='active')
    progress = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_plan_data(self):
        if self.plan_data:
            return json.loads(self.plan_data)
        return {}
    
    def set_plan_data(self, data):
        self.plan_data = json.dumps(data)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'daily_calories': self.daily_calories,
            'duration_weeks': self.duration_weeks,
            'macros': {
                'protein': self.protein_percentage,
                'carbs': self.carbs_percentage,
                'fats': self.fats_percentage
            },
            'status': self.status,
            'progress': self.progress,
            'plan_data': self.get_plan_data(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ProgressEntry(db.Model):
    __tablename__ = 'progress_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float)
    body_fat = db.Column(db.Float)
    muscle_mass = db.Column(db.Float)
    
    # Medidas corporales (en cm)
    chest = db.Column(db.Float)
    waist = db.Column(db.Float)
    hips = db.Column(db.Float)
    arms = db.Column(db.Float)
    thighs = db.Column(db.Float)
    
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'weight': self.weight,
            'body_fat': self.body_fat,
            'muscle_mass': self.muscle_mass,
            'measurements': {
                'chest': self.chest,
                'waist': self.waist,
                'hips': self.hips,
                'arms': self.arms,
                'thighs': self.thighs
            },
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

