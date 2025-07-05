from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import openai
import json
from app import db
from models.user import User, WorkoutPlan, NutritionPlan

ai_bp = Blueprint('ai', __name__)

def get_openai_client():
    """Obtiene el cliente de OpenAI configurado"""
    api_key = current_app.config.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not configured")
    
    openai.api_key = api_key
    return openai

@ai_bp.route('/generate-workout', methods=['POST'])
@jwt_required()
def generate_workout_plan():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        
        # Parámetros del plan
        fitness_goal = data.get('fitness_goal', user.fitness_goal or 'general_fitness')
        activity_level = data.get('activity_level', user.activity_level or 'beginner')
        duration_weeks = data.get('duration_weeks', 4)
        workouts_per_week = data.get('workouts_per_week', 3)
        equipment_available = data.get('equipment_available', ['bodyweight'])
        focus_areas = data.get('focus_areas', [])
        
        # Crear prompt para OpenAI
        prompt = f"""
        Crea un plan de entrenamiento personalizado con las siguientes especificaciones:
        
        Usuario:
        - Objetivo: {fitness_goal}
        - Nivel: {activity_level}
        - Edad: {user.age or 'No especificada'}
        - Género: {user.gender or 'No especificado'}
        
        Plan:
        - Duración: {duration_weeks} semanas
        - Entrenamientos por semana: {workouts_per_week}
        - Equipo disponible: {', '.join(equipment_available)}
        - Áreas de enfoque: {', '.join(focus_areas) if focus_areas else 'General'}
        
        Genera un plan estructurado en formato JSON con la siguiente estructura:
        {{
            "name": "Nombre del plan",
            "description": "Descripción del plan",
            "difficulty": "beginner/intermediate/advanced",
            "weeks": [
                {{
                    "week": 1,
                    "workouts": [
                        {{
                            "day": "Lunes",
                            "name": "Nombre del entrenamiento",
                            "duration_minutes": 45,
                            "exercises": [
                                {{
                                    "name": "Nombre del ejercicio",
                                    "sets": 3,
                                    "reps": "8-10",
                                    "rest_seconds": 90,
                                    "instructions": "Instrucciones del ejercicio"
                                }}
                            ]
                        }}
                    ]
                }}
            ]
        }}
        
        Asegúrate de que el plan sea progresivo, seguro y apropiado para el nivel del usuario.
        """
        
        # Llamar a OpenAI
        client = get_openai_client()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un entrenador personal experto que crea planes de entrenamiento personalizados. Responde solo con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parsear respuesta
        plan_content = response.choices[0].message.content.strip()
        
        # Intentar parsear JSON
        try:
            plan_data = json.loads(plan_content)
        except json.JSONDecodeError:
            # Si no es JSON válido, crear un plan básico
            plan_data = {
                "name": f"Plan de {fitness_goal.replace('_', ' ').title()}",
                "description": f"Plan personalizado de {duration_weeks} semanas para {fitness_goal}",
                "difficulty": activity_level,
                "weeks": []
            }
        
        # Crear el plan en la base de datos
        workout_plan = WorkoutPlan(
            user_id=user_id,
            name=plan_data.get('name', f'Plan de Entrenamiento - {fitness_goal}'),
            description=plan_data.get('description', 'Plan generado con IA'),
            duration_weeks=duration_weeks,
            workouts_per_week=workouts_per_week,
            difficulty=plan_data.get('difficulty', activity_level)
        )
        
        workout_plan.set_plan_data(plan_data)
        
        db.session.add(workout_plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Plan de entrenamiento generado exitosamente',
            'plan': workout_plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error generating workout plan: {str(e)}")
        return jsonify({'error': 'Error generando el plan de entrenamiento'}), 500

@ai_bp.route('/generate-nutrition', methods=['POST'])
@jwt_required()
def generate_nutrition_plan():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        
        # Parámetros del plan
        goal = data.get('goal', 'maintenance')
        daily_calories = data.get('daily_calories', 2000)
        dietary_restrictions = data.get('dietary_restrictions', user.dietary_restrictions or '')
        meals_per_day = data.get('meals_per_day', 3)
        duration_weeks = data.get('duration_weeks', 4)
        allergies = data.get('allergies', '')
        
        # Calcular macronutrientes según el objetivo
        if goal == 'weight_loss':
            protein_pct, carbs_pct, fats_pct = 35, 35, 30
        elif goal == 'muscle_gain':
            protein_pct, carbs_pct, fats_pct = 30, 45, 25
        elif goal == 'performance':
            protein_pct, carbs_pct, fats_pct = 25, 50, 25
        else:  # maintenance
            protein_pct, carbs_pct, fats_pct = 25, 45, 30
        
        # Crear prompt para OpenAI
        prompt = f"""
        Crea un plan nutricional personalizado con las siguientes especificaciones:
        
        Usuario:
        - Objetivo: {goal}
        - Calorías diarias: {daily_calories}
        - Restricciones dietéticas: {dietary_restrictions or 'Ninguna'}
        - Alergias: {allergies or 'Ninguna'}
        - Edad: {user.age or 'No especificada'}
        - Peso: {user.weight or 'No especificado'} kg
        - Altura: {user.height or 'No especificada'} cm
        
        Plan:
        - Comidas por día: {meals_per_day}
        - Duración: {duration_weeks} semanas
        - Distribución de macronutrientes: {protein_pct}% proteína, {carbs_pct}% carbohidratos, {fats_pct}% grasas
        
        Genera un plan estructurado en formato JSON con la siguiente estructura:
        {{
            "name": "Nombre del plan",
            "description": "Descripción del plan",
            "daily_meals": [
                {{
                    "name": "Desayuno",
                    "time": "08:00",
                    "calories": 400,
                    "foods": [
                        {{
                            "name": "Avena con frutas",
                            "quantity": "1 taza",
                            "calories": 250,
                            "protein": 8,
                            "carbs": 45,
                            "fats": 5
                        }}
                    ]
                }}
            ],
            "weekly_variations": [
                {{
                    "week": 1,
                    "notes": "Semana de adaptación",
                    "meal_suggestions": ["Sugerencias específicas para esta semana"]
                }}
            ]
        }}
        
        Asegúrate de que el plan sea balanceado, variado y apropiado para el objetivo del usuario.
        """
        
        # Llamar a OpenAI
        client = get_openai_client()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un nutricionista experto que crea planes alimentarios personalizados. Responde solo con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parsear respuesta
        plan_content = response.choices[0].message.content.strip()
        
        # Intentar parsear JSON
        try:
            plan_data = json.loads(plan_content)
        except json.JSONDecodeError:
            # Si no es JSON válido, crear un plan básico
            plan_data = {
                "name": f"Plan Nutricional - {goal.replace('_', ' ').title()}",
                "description": f"Plan personalizado de {duration_weeks} semanas para {goal}",
                "daily_meals": [],
                "weekly_variations": []
            }
        
        # Crear el plan en la base de datos
        nutrition_plan = NutritionPlan(
            user_id=user_id,
            name=plan_data.get('name', f'Plan Nutricional - {goal}'),
            description=plan_data.get('description', 'Plan generado con IA'),
            daily_calories=daily_calories,
            duration_weeks=duration_weeks,
            protein_percentage=protein_pct,
            carbs_percentage=carbs_pct,
            fats_percentage=fats_pct
        )
        
        nutrition_plan.set_plan_data(plan_data)
        
        db.session.add(nutrition_plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Plan nutricional generado exitosamente',
            'plan': nutrition_plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error generating nutrition plan: {str(e)}")
        return jsonify({'error': 'Error generando el plan nutricional'}), 500

@ai_bp.route('/chat', methods=['POST'])
@jwt_required()
def ai_chat():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Mensaje requerido'}), 400
        
        # Crear contexto del usuario
        user_context = f"""
        Usuario: {user.name}
        Objetivo: {user.fitness_goal or 'No especificado'}
        Nivel: {user.activity_level or 'No especificado'}
        Edad: {user.age or 'No especificada'}
        Peso: {user.weight or 'No especificado'} kg
        Altura: {user.height or 'No especificada'} cm
        """
        
        # Llamar a OpenAI
        client = get_openai_client()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Eres un asistente de fitness y nutrición experto. Ayuda al usuario con consejos personalizados basados en su información: {user_context}"},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        return jsonify({
            'response': ai_response
        }), 200
        
    except Exception as e:
        print(f"Error in AI chat: {str(e)}")
        return jsonify({'error': 'Error procesando la consulta'}), 500

