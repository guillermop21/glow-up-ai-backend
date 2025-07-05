from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from models.user import User, WorkoutPlan

workout_bp = Blueprint('workouts', __name__)

@workout_bp.route('/', methods=['GET'])
@jwt_required()
def get_workout_plans():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Obtener parámetros de filtro
        status = request.args.get('status')
        difficulty = request.args.get('difficulty')
        
        # Construir query
        query = WorkoutPlan.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        
        plans = query.order_by(WorkoutPlan.created_at.desc()).all()
        
        return jsonify({
            'plans': [plan.to_dict() for plan in plans]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@workout_bp.route('/<int:plan_id>', methods=['GET'])
@jwt_required()
def get_workout_plan(plan_id):
    try:
        user_id = get_jwt_identity()
        plan = WorkoutPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
        
        return jsonify({'plan': plan.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@workout_bp.route('/', methods=['POST'])
@jwt_required()
def create_workout_plan():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('name'):
            return jsonify({'error': 'El nombre del plan es requerido'}), 400
        
        plan = WorkoutPlan(
            user_id=user_id,
            name=data['name'],
            description=data.get('description', ''),
            duration_weeks=data.get('duration_weeks', 4),
            workouts_per_week=data.get('workouts_per_week', 3),
            difficulty=data.get('difficulty', 'beginner')
        )
        
        # Si se proporciona plan_data, guardarlo
        if data.get('plan_data'):
            plan.set_plan_data(data['plan_data'])
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Plan creado exitosamente',
            'plan': plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@workout_bp.route('/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_workout_plan(plan_id):
    try:
        user_id = get_jwt_identity()
        plan = WorkoutPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        allowed_fields = ['name', 'description', 'status', 'progress']
        for field in allowed_fields:
            if field in data:
                setattr(plan, field, data[field])
        
        # Actualizar plan_data si se proporciona
        if 'plan_data' in data:
            plan.set_plan_data(data['plan_data'])
        
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Plan actualizado exitosamente',
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@workout_bp.route('/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_workout_plan(plan_id):
    try:
        user_id = get_jwt_identity()
        plan = WorkoutPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
        
        db.session.delete(plan)
        db.session.commit()
        
        return jsonify({'message': 'Plan eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@workout_bp.route('/<int:plan_id>/start', methods=['POST'])
@jwt_required()
def start_workout_plan(plan_id):
    try:
        user_id = get_jwt_identity()
        plan = WorkoutPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
        
        plan.status = 'active'
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Plan iniciado exitosamente',
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@workout_bp.route('/<int:plan_id>/complete', methods=['POST'])
@jwt_required()
def complete_workout_plan(plan_id):
    try:
        user_id = get_jwt_identity()
        plan = WorkoutPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
        
        plan.status = 'completed'
        plan.progress = 100.0
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Plan completado exitosamente',
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@workout_bp.route('/<int:plan_id>/progress', methods=['POST'])
@jwt_required()
def update_workout_progress(plan_id):
    try:
        user_id = get_jwt_identity()
        plan = WorkoutPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        
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

@workout_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_workout_stats():
    try:
        user_id = get_jwt_identity()
        
        # Obtener estadísticas de planes de entrenamiento
        total_plans = WorkoutPlan.query.filter_by(user_id=user_id).count()
        active_plans = WorkoutPlan.query.filter_by(user_id=user_id, status='active').count()
        completed_plans = WorkoutPlan.query.filter_by(user_id=user_id, status='completed').count()
        
        # Calcular progreso promedio
        plans = WorkoutPlan.query.filter_by(user_id=user_id).all()
        avg_progress = sum(plan.progress for plan in plans) / len(plans) if plans else 0
        
        # Obtener plan más reciente
        latest_plan = WorkoutPlan.query.filter_by(user_id=user_id).order_by(WorkoutPlan.created_at.desc()).first()
        
        stats = {
            'total_plans': total_plans,
            'active_plans': active_plans,
            'completed_plans': completed_plans,
            'average_progress': round(avg_progress, 1),
            'latest_plan': latest_plan.to_dict() if latest_plan else None
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

