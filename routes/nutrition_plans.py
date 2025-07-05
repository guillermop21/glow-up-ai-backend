from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from models.user import User, NutritionPlan

nutrition_bp = Blueprint('nutrition', __name__)

@nutrition_bp.route('/', methods=['GET'])
@jwt_required()
def get_nutrition_plans():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Obtener parámetros de filtro
        status = request.args.get('status')
        
        # Construir query
        query = NutritionPlan.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        plans = query.order_by(NutritionPlan.created_at.desc()).all()
        
        return jsonify({
            'plans': [plan.to_dict() for plan in plans]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@nutrition_bp.route('/<int:plan_id>', methods=['GET'])
@jwt_required()
def get_nutrition_plan(plan_id):
    try:
        user_id = get_jwt_identity()
        plan = NutritionPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
        
        return jsonify({'plan': plan.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@nutrition_bp.route('/', methods=['POST'])
@jwt_required()
def create_nutrition_plan():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('name'):
            return jsonify({'error': 'El nombre del plan es requerido'}), 400
        
        plan = NutritionPlan(
            user_id=user_id,
            name=data['name'],
            description=data.get('description', ''),
            daily_calories=data.get('daily_calories', 2000),
            duration_weeks=data.get('duration_weeks', 4),
            protein_percentage=data.get('protein_percentage', 25),
            carbs_percentage=data.get('carbs_percentage', 45),
            fats_percentage=data.get('fats_percentage', 30)
        )
        
        # Si se proporciona plan_data, guardarlo
        if data.get('plan_data'):
            plan.set_plan_data(data['plan_data'])
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Plan nutricional creado exitosamente',
            'plan': plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@nutrition_bp.route('/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_nutrition_plan(plan_id):
    try:
        user_id = get_jwt_identity()
        plan = NutritionPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        allowed_fields = ['name', 'description', 'daily_calories', 'status', 'progress']
        for field in allowed_fields:
            if field in data:
                setattr(plan, field, data[field])
        
        # Actualizar macronutrientes
        if 'protein_percentage' in data:
            plan.protein_percentage = data['protein_percentage']
        if 'carbs_percentage' in data:
            plan.carbs_percentage = data['carbs_percentage']
        if 'fats_percentage' in data:
            plan.fats_percentage = data['fats_percentage']
        
        # Actualizar plan_data si se proporciona
        if 'plan_data' in data:
            plan.set_plan_data(data['plan_data'])
        
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Plan nutricional actualizado exitosamente',
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@nutrition_bp.route('/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_nutrition_plan(plan_id):
    try:
        user_id = get_jwt_identity()
        plan = NutritionPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
        
        db.session.delete(plan)
        db.session.commit()
        
        return jsonify({'message': 'Plan nutricional eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@nutrition_bp.route('/<int:plan_id>/start', methods=['POST'])
@jwt_required()
def start_nutrition_plan(plan_id):
    try:
        user_id = get_jwt_identity()
        plan = NutritionPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
        
        plan.status = 'active'
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Plan nutricional iniciado exitosamente',
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@nutrition_bp.route('/<int:plan_id>/complete', methods=['POST'])
@jwt_required()
def complete_nutrition_plan(plan_id):
    try:
        user_id = get_jwt_identity()
        plan = NutritionPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
        
        plan.status = 'completed'
        plan.progress = 100.0
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Plan nutricional completado exitosamente',
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@nutrition_bp.route('/<int:plan_id>/progress', methods=['POST'])
@jwt_required()
def update_nutrition_progress(plan_id):
    try:
        user_id = get_jwt_identity()
        plan = NutritionPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
        
        data = request.get_json()
        progress = data.get('progress')
        
        if progress is None or not (0 <= progress <= 100):
            return jsonify({'error': 'Progreso debe estar entre 0 y 100'}), 400
        
        plan.progress = progress
        
        # Actualizar estado basado en progreso
        if progress == 100:
            plan.status = 'completed'
        elif progress > 0:
            plan.status = 'active'
        
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Progreso actualizado exitosamente',
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@nutrition_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_nutrition_stats():
    try:
        user_id = get_jwt_identity()
        
        # Obtener estadísticas de planes nutricionales
        total_plans = NutritionPlan.query.filter_by(user_id=user_id).count()
        active_plans = NutritionPlan.query.filter_by(user_id=user_id, status='active').count()
        completed_plans = NutritionPlan.query.filter_by(user_id=user_id, status='completed').count()
        
        # Calcular progreso promedio
        plans = NutritionPlan.query.filter_by(user_id=user_id).all()
        avg_progress = sum(plan.progress for plan in plans) / len(plans) if plans else 0
        
        # Calcular calorías promedio
        avg_calories = sum(plan.daily_calories for plan in plans if plan.daily_calories) / len([p for p in plans if p.daily_calories]) if plans else 0
        
        # Obtener plan más reciente
        latest_plan = NutritionPlan.query.filter_by(user_id=user_id).order_by(NutritionPlan.created_at.desc()).first()
        
        stats = {
            'total_plans': total_plans,
            'active_plans': active_plans,
            'completed_plans': completed_plans,
            'average_progress': round(avg_progress, 1),
            'average_calories': round(avg_calories, 0),
            'latest_plan': latest_plan.to_dict() if latest_plan else None
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@nutrition_bp.route('/calculate-calories', methods=['POST'])
@jwt_required()
def calculate_calories():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        
        # Obtener datos del usuario o del request
        age = data.get('age', user.age)
        gender = data.get('gender', user.gender)
        height = data.get('height', user.height)  # cm
        weight = data.get('weight', user.weight)  # kg
        activity_level = data.get('activity_level', user.activity_level)
        goal = data.get('goal', 'maintenance')
        
        if not all([age, gender, height, weight]):
            return jsonify({'error': 'Edad, género, altura y peso son requeridos'}), 400
        
        # Calcular BMR usando la fórmula de Mifflin-St Jeor
        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:  # female
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Factores de actividad
        activity_factors = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        activity_factor = activity_factors.get(activity_level, 1.2)
        maintenance_calories = bmr * activity_factor
        
        # Ajustar según el objetivo
        if goal == 'weight_loss':
            target_calories = maintenance_calories - 500  # Déficit de 500 cal
        elif goal == 'muscle_gain':
            target_calories = maintenance_calories + 300  # Superávit de 300 cal
        else:  # maintenance
            target_calories = maintenance_calories
        
        # Calcular macronutrientes recomendados
        if goal == 'weight_loss':
            protein_pct, carbs_pct, fats_pct = 35, 35, 30
        elif goal == 'muscle_gain':
            protein_pct, carbs_pct, fats_pct = 30, 45, 25
        else:  # maintenance
            protein_pct, carbs_pct, fats_pct = 25, 45, 30
        
        # Calcular gramos de macronutrientes
        protein_grams = (target_calories * protein_pct / 100) / 4
        carbs_grams = (target_calories * carbs_pct / 100) / 4
        fats_grams = (target_calories * fats_pct / 100) / 9
        
        result = {
            'bmr': round(bmr, 0),
            'maintenance_calories': round(maintenance_calories, 0),
            'target_calories': round(target_calories, 0),
            'macros': {
                'protein': {
                    'percentage': protein_pct,
                    'grams': round(protein_grams, 1)
                },
                'carbs': {
                    'percentage': carbs_pct,
                    'grams': round(carbs_grams, 1)
                },
                'fats': {
                    'percentage': fats_pct,
                    'grams': round(fats_grams, 1)
                }
            }
        }
        
        return jsonify({'calculation': result}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

