from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc
from app import db
from models.user import User, ProgressEntry
import statistics

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/', methods=['GET'])
@jwt_required()
def get_progress_entries():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Obtener parámetros de filtro
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', type=int)
        
        # Construir query
        query = ProgressEntry.query.filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(ProgressEntry.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(ProgressEntry.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        query = query.order_by(desc(ProgressEntry.date))
        
        if limit:
            query = query.limit(limit)
        
        entries = query.all()
        
        return jsonify({
            'entries': [entry.to_dict() for entry in entries],
            'total': len(entries)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@progress_bp.route('/<int:entry_id>', methods=['GET'])
@jwt_required()
def get_progress_entry(entry_id):
    try:
        user_id = get_jwt_identity()
        entry = ProgressEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        
        if not entry:
            return jsonify({'error': 'Registro no encontrado'}), 404
        
        return jsonify({'entry': entry.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@progress_bp.route('/', methods=['POST'])
@jwt_required()
def create_progress_entry():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        
        # Validar que al menos un campo de medición esté presente
        measurement_fields = ['weight', 'body_fat', 'muscle_mass', 'chest', 'waist', 'hips', 'arms', 'thighs']
        if not any(data.get(field) for field in measurement_fields):
            return jsonify({'error': 'Al menos una medición es requerida'}), 400
        
        # Verificar si ya existe una entrada para esta fecha
        entry_date = datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        existing_entry = ProgressEntry.query.filter_by(user_id=user_id, date=entry_date).first()
        
        if existing_entry:
            return jsonify({'error': 'Ya existe un registro para esta fecha'}), 400
        
        entry = ProgressEntry(
            user_id=user_id,
            date=entry_date,
            weight=data.get('weight'),
            body_fat=data.get('body_fat'),
            muscle_mass=data.get('muscle_mass'),
            chest=data.get('chest'),
            waist=data.get('waist'),
            hips=data.get('hips'),
            arms=data.get('arms'),
            thighs=data.get('thighs'),
            notes=data.get('notes', '')
        )
        
        db.session.add(entry)
        db.session.commit()
        
        # Actualizar el peso del usuario si se proporciona
        if data.get('weight'):
            user.weight = data['weight']
            db.session.commit()
        
        return jsonify({
            'message': 'Registro de progreso creado exitosamente',
            'entry': entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@progress_bp.route('/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_progress_entry(entry_id):
    try:
        user_id = get_jwt_identity()
        entry = ProgressEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        
        if not entry:
            return jsonify({'error': 'Registro no encontrado'}), 404
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        allowed_fields = ['weight', 'body_fat', 'muscle_mass', 'chest', 'waist', 'hips', 'arms', 'thighs', 'notes']
        for field in allowed_fields:
            if field in data:
                setattr(entry, field, data[field])
        
        # Actualizar fecha si se proporciona
        if 'date' in data:
            new_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            # Verificar que no haya conflicto con otra entrada
            existing_entry = ProgressEntry.query.filter_by(user_id=user_id, date=new_date).filter(ProgressEntry.id != entry_id).first()
            if existing_entry:
                return jsonify({'error': 'Ya existe un registro para esta fecha'}), 400
            entry.date = new_date
        
        db.session.commit()
        
        return jsonify({
            'message': 'Registro actualizado exitosamente',
            'entry': entry.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@progress_bp.route('/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_progress_entry(entry_id):
    try:
        user_id = get_jwt_identity()
        entry = ProgressEntry.query.filter_by(id=entry_id, user_id=user_id).first()
        
        if not entry:
            return jsonify({'error': 'Registro no encontrado'}), 404
        
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({'message': 'Registro eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@progress_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_progress_stats():
    try:
        user_id = get_jwt_identity()
        
        # Obtener todas las entradas del usuario
        entries = ProgressEntry.query.filter_by(user_id=user_id).order_by(ProgressEntry.date).all()
        
        if not entries:
            return jsonify({
                'stats': {
                    'total_entries': 0,
                    'current_streak': 0,
                    'weight_change': 0,
                    'body_fat_change': 0,
                    'muscle_mass_change': 0,
                    'measurements_change': {},
                    'trends': {}
                }
            }), 200
        
        # Calcular estadísticas básicas
        total_entries = len(entries)
        
        # Calcular racha actual
        current_streak = calculate_current_streak(entries)
        
        # Calcular cambios desde el primer registro
        first_entry = entries[0]
        latest_entry = entries[-1]
        
        weight_change = (latest_entry.weight - first_entry.weight) if (latest_entry.weight and first_entry.weight) else 0
        body_fat_change = (latest_entry.body_fat - first_entry.body_fat) if (latest_entry.body_fat and first_entry.body_fat) else 0
        muscle_mass_change = (latest_entry.muscle_mass - first_entry.muscle_mass) if (latest_entry.muscle_mass and first_entry.muscle_mass) else 0
        
        # Calcular cambios en medidas corporales
        measurements_change = {}
        measurement_fields = ['chest', 'waist', 'hips', 'arms', 'thighs']
        for field in measurement_fields:
            first_val = getattr(first_entry, field)
            latest_val = getattr(latest_entry, field)
            if first_val and latest_val:
                measurements_change[field] = latest_val - first_val
        
        # Calcular tendencias (últimos 30 días)
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_entries = [e for e in entries if e.date >= thirty_days_ago]
        trends = calculate_trends(recent_entries)
        
        # Calcular promedios y rangos
        averages = calculate_averages(entries)
        
        # Calcular BMI si hay datos
        bmi_data = calculate_bmi_progression(entries)
        
        stats = {
            'total_entries': total_entries,
            'current_streak': current_streak,
            'weight_change': round(weight_change, 1),
            'body_fat_change': round(body_fat_change, 1),
            'muscle_mass_change': round(muscle_mass_change, 1),
            'measurements_change': {k: round(v, 1) for k, v in measurements_change.items()},
            'trends': trends,
            'averages': averages,
            'bmi_data': bmi_data,
            'date_range': {
                'first': first_entry.date.isoformat(),
                'latest': latest_entry.date.isoformat(),
                'days_tracked': (latest_entry.date - first_entry.date).days + 1
            }
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@progress_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_progress_analytics():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Obtener parámetros
        period = request.args.get('period', 'month')  # week, month, quarter, year
        metric = request.args.get('metric', 'weight')  # weight, body_fat, muscle_mass, measurements
        
        # Calcular fechas según el período
        end_date = date.today()
        if period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'quarter':
            start_date = end_date - timedelta(days=90)
        else:  # year
            start_date = end_date - timedelta(days=365)
        
        # Obtener entradas del período
        entries = ProgressEntry.query.filter_by(user_id=user_id)\
            .filter(ProgressEntry.date >= start_date)\
            .filter(ProgressEntry.date <= end_date)\
            .order_by(ProgressEntry.date).all()
        
        if not entries:
            return jsonify({
                'analytics': {
                    'period': period,
                    'metric': metric,
                    'data_points': [],
                    'insights': []
                }
            }), 200
        
        # Generar puntos de datos
        data_points = []
        for entry in entries:
            point = {
                'date': entry.date.isoformat(),
                'value': getattr(entry, metric) if hasattr(entry, metric) else None
            }
            if point['value'] is not None:
                data_points.append(point)
        
        # Generar insights inteligentes
        insights = generate_insights(entries, metric, user)
        
        # Calcular estadísticas del período
        period_stats = calculate_period_stats(data_points, metric)
        
        analytics = {
            'period': period,
            'metric': metric,
            'data_points': data_points,
            'insights': insights,
            'period_stats': period_stats,
            'recommendations': generate_recommendations(entries, metric, user)
        }
        
        return jsonify({'analytics': analytics}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@progress_bp.route('/goals', methods=['GET'])
@jwt_required()
def get_progress_goals():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Obtener la entrada más reciente
        latest_entry = ProgressEntry.query.filter_by(user_id=user_id)\
            .order_by(desc(ProgressEntry.date)).first()
        
        # Generar objetivos inteligentes basados en el perfil del usuario
        goals = generate_smart_goals(user, latest_entry)
        
        return jsonify({'goals': goals}), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

# Funciones auxiliares para cálculos avanzados

def calculate_current_streak(entries):
    """Calcula la racha actual de días consecutivos con registros"""
    if not entries:
        return 0
    
    # Ordenar por fecha descendente
    sorted_entries = sorted(entries, key=lambda x: x.date, reverse=True)
    current_date = date.today()
    streak = 0
    
    for entry in sorted_entries:
        days_diff = (current_date - entry.date).days
        if days_diff == streak:
            streak += 1
            current_date = entry.date
        else:
            break
    
    return streak

def calculate_trends(entries):
    """Calcula tendencias en los datos recientes"""
    if len(entries) < 2:
        return {}
    
    trends = {}
    metrics = ['weight', 'body_fat', 'muscle_mass']
    
    for metric in metrics:
        values = [getattr(e, metric) for e in entries if getattr(e, metric) is not None]
        if len(values) >= 2:
            # Calcular tendencia simple (pendiente)
            x = list(range(len(values)))
            if len(values) > 1:
                slope = (values[-1] - values[0]) / (len(values) - 1)
                trends[metric] = {
                    'direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                    'rate': round(slope, 2),
                    'confidence': min(len(values) / 10, 1.0)  # Más datos = más confianza
                }
    
    return trends

def calculate_averages(entries):
    """Calcula promedios de las métricas"""
    averages = {}
    metrics = ['weight', 'body_fat', 'muscle_mass', 'chest', 'waist', 'hips', 'arms', 'thighs']
    
    for metric in metrics:
        values = [getattr(e, metric) for e in entries if getattr(e, metric) is not None]
        if values:
            averages[metric] = {
                'mean': round(statistics.mean(values), 1),
                'median': round(statistics.median(values), 1),
                'min': round(min(values), 1),
                'max': round(max(values), 1)
            }
    
    return averages

def calculate_bmi_progression(entries):
    """Calcula la progresión del BMI si hay datos de peso y altura"""
    bmi_data = []
    
    for entry in entries:
        if entry.weight and entry.user.height:
            height_m = entry.user.height / 100  # convertir cm a metros
            bmi = entry.weight / (height_m ** 2)
            bmi_data.append({
                'date': entry.date.isoformat(),
                'bmi': round(bmi, 1),
                'category': get_bmi_category(bmi)
            })
    
    return bmi_data

def get_bmi_category(bmi):
    """Determina la categoría del BMI"""
    if bmi < 18.5:
        return 'Bajo peso'
    elif bmi < 25:
        return 'Normal'
    elif bmi < 30:
        return 'Sobrepeso'
    else:
        return 'Obesidad'

def generate_insights(entries, metric, user):
    """Genera insights inteligentes basados en los datos"""
    insights = []
    
    if len(entries) < 2:
        return insights
    
    # Insight sobre consistencia
    days_with_data = len(entries)
    total_days = (entries[-1].date - entries[0].date).days + 1
    consistency = days_with_data / total_days
    
    if consistency > 0.8:
        insights.append({
            'type': 'positive',
            'message': f'¡Excelente! Has sido muy consistente registrando tu progreso ({consistency*100:.0f}% de los días).'
        })
    elif consistency < 0.3:
        insights.append({
            'type': 'suggestion',
            'message': 'Intenta ser más consistente con tus registros para obtener mejores insights sobre tu progreso.'
        })
    
    # Insights específicos por métrica
    if metric == 'weight' and user.fitness_goal:
        weight_values = [e.weight for e in entries if e.weight]
        if len(weight_values) >= 2:
            change = weight_values[-1] - weight_values[0]
            if user.fitness_goal == 'weight_loss' and change < -1:
                insights.append({
                    'type': 'positive',
                    'message': f'¡Vas por buen camino! Has perdido {abs(change):.1f} kg hacia tu objetivo.'
                })
            elif user.fitness_goal == 'muscle_gain' and change > 1:
                insights.append({
                    'type': 'positive',
                    'message': f'¡Excelente progreso! Has ganado {change:.1f} kg de masa.'
                })
    
    return insights

def calculate_period_stats(data_points, metric):
    """Calcula estadísticas del período"""
    if not data_points:
        return {}
    
    values = [point['value'] for point in data_points]
    
    return {
        'total_change': round(values[-1] - values[0], 1) if len(values) > 1 else 0,
        'average': round(statistics.mean(values), 1),
        'best_value': round(max(values), 1),
        'worst_value': round(min(values), 1),
        'volatility': round(statistics.stdev(values), 1) if len(values) > 1 else 0
    }

def generate_recommendations(entries, metric, user):
    """Genera recomendaciones personalizadas"""
    recommendations = []
    
    if not entries:
        recommendations.append("Comienza a registrar tu progreso regularmente para obtener recomendaciones personalizadas.")
        return recommendations
    
    # Recomendaciones basadas en el objetivo del usuario
    if user.fitness_goal == 'weight_loss':
        recommendations.append("Mantén un déficit calórico consistente y registra tu peso semanalmente.")
        recommendations.append("Combina cardio con entrenamiento de fuerza para mejores resultados.")
    elif user.fitness_goal == 'muscle_gain':
        recommendations.append("Asegúrate de consumir suficientes proteínas (1.6-2.2g por kg de peso corporal).")
        recommendations.append("Registra tus medidas corporales además del peso para ver el progreso muscular.")
    
    # Recomendaciones basadas en la consistencia
    if len(entries) < 5:
        recommendations.append("Intenta registrar tu progreso al menos 2-3 veces por semana para mejores insights.")
    
    return recommendations

def generate_smart_goals(user, latest_entry):
    """Genera objetivos SMART basados en el perfil del usuario"""
    goals = []
    
    if not latest_entry:
        return [{
            'type': 'tracking',
            'title': 'Comenzar seguimiento',
            'description': 'Registra tu primera medición para establecer objetivos personalizados',
            'target': 'Crear primer registro',
            'deadline': 'Esta semana'
        }]
    
    # Objetivos basados en el fitness goal del usuario
    if user.fitness_goal == 'weight_loss' and latest_entry.weight:
        target_weight = latest_entry.weight * 0.95  # 5% de pérdida
        goals.append({
            'type': 'weight_loss',
            'title': 'Pérdida de peso saludable',
            'description': f'Reducir peso de {latest_entry.weight}kg a {target_weight:.1f}kg',
            'target': f'{target_weight:.1f} kg',
            'deadline': '8 semanas',
            'current': latest_entry.weight,
            'progress': 0
        })
    
    elif user.fitness_goal == 'muscle_gain' and latest_entry.muscle_mass:
        target_muscle = latest_entry.muscle_mass * 1.05  # 5% de ganancia
        goals.append({
            'type': 'muscle_gain',
            'title': 'Ganancia de masa muscular',
            'description': f'Aumentar masa muscular de {latest_entry.muscle_mass}kg a {target_muscle:.1f}kg',
            'target': f'{target_muscle:.1f} kg',
            'deadline': '12 semanas',
            'current': latest_entry.muscle_mass,
            'progress': 0
        })
    
    # Objetivo de consistencia
    goals.append({
        'type': 'consistency',
        'title': 'Consistencia en el seguimiento',
        'description': 'Registrar progreso 3 veces por semana',
        'target': '12 registros',
        'deadline': '4 semanas',
        'current': 0,
        'progress': 0
    })
    
    return goals

