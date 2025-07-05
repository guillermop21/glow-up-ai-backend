from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        
        # Validar email si se está actualizando
        if 'email' in data and data['email'] != user.email:
            new_email = data['email'].strip().lower()
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user:
                return jsonify({'error': 'El email ya está en uso'}), 400
            user.email = new_email
        
        # Actualizar otros campos
        user.update_from_dict(data)
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil actualizado exitosamente',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Obtener estadísticas del usuario
        workout_plans_count = len(user.workout_plans)
        nutrition_plans_count = len(user.nutrition_plans)
        progress_entries_count = len(user.progress_entries)
        
        # Calcular racha actual (días consecutivos con actividad)
        current_streak = 0
        if user.progress_entries:
            # Ordenar entradas por fecha descendente
            sorted_entries = sorted(user.progress_entries, key=lambda x: x.date, reverse=True)
            current_date = datetime.now().date()
            
            for entry in sorted_entries:
                if entry.date == current_date or (current_date - entry.date).days == current_streak:
                    current_streak += 1
                    current_date = entry.date
                else:
                    break
        
        # Calcular progreso de peso si hay entradas
        weight_change = 0
        if len(user.progress_entries) >= 2:
            sorted_entries = sorted(user.progress_entries, key=lambda x: x.date)
            first_weight = next((e.weight for e in sorted_entries if e.weight), None)
            last_weight = next((e.weight for e in reversed(sorted_entries) if e.weight), None)
            if first_weight and last_weight:
                weight_change = last_weight - first_weight
        
        stats = {
            'workout_plans': workout_plans_count,
            'nutrition_plans': nutrition_plans_count,
            'progress_entries': progress_entries_count,
            'current_streak': current_streak,
            'weight_change': round(weight_change, 1) if weight_change else 0,
            'member_since': user.created_at.isoformat() if user.created_at else None,
            'last_activity': user.last_login.isoformat() if user.last_login else None
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@user_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_subscription():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        subscription = {
            'type': user.subscription_type or 'basic',
            'expires': user.subscription_expires.isoformat() if user.subscription_expires else None,
            'is_active': True if not user.subscription_expires or user.subscription_expires > datetime.utcnow() else False
        }
        
        return jsonify({'subscription': subscription}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@user_bp.route('/subscription', methods=['POST'])
@jwt_required()
def update_subscription():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        subscription_type = data.get('type')
        
        if subscription_type not in ['basic', 'premium', 'pro']:
            return jsonify({'error': 'Tipo de suscripción inválido'}), 400
        
        user.subscription_type = subscription_type
        
        # Establecer fecha de expiración (30 días desde ahora)
        if subscription_type != 'basic':
            user.subscription_expires = datetime.utcnow() + timedelta(days=30)
        else:
            user.subscription_expires = None
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Suscripción actualizada exitosamente',
            'subscription': {
                'type': user.subscription_type,
                'expires': user.subscription_expires.isoformat() if user.subscription_expires else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@user_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_account():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Eliminar usuario (las relaciones se eliminan en cascada)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Cuenta eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

