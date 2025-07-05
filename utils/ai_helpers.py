import openai
import json
import logging
from typing import Dict, List, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIWorkoutGenerator:
    """Generador de planes de entrenamiento con IA"""
    
    @staticmethod
    def create_workout_prompt(user_data: Dict, plan_params: Dict) -> str:
        """Crea un prompt optimizado para generar planes de entrenamiento"""
        
        # Información del usuario
        user_info = f"""
        PERFIL DEL USUARIO:
        - Edad: {user_data.get('age', 'No especificada')} años
        - Género: {user_data.get('gender', 'No especificado')}
        - Peso: {user_data.get('weight', 'No especificado')} kg
        - Altura: {user_data.get('height', 'No especificada')} cm
        - Nivel de experiencia: {plan_params.get('activity_level', 'principiante')}
        - Objetivo principal: {plan_params.get('fitness_goal', 'fitness general')}
        """
        
        # Parámetros del plan
        plan_info = f"""
        ESPECIFICACIONES DEL PLAN:
        - Duración: {plan_params.get('duration_weeks', 4)} semanas
        - Entrenamientos por semana: {plan_params.get('workouts_per_week', 3)}
        - Equipo disponible: {', '.join(plan_params.get('equipment_available', ['peso corporal']))}
        - Áreas de enfoque: {', '.join(plan_params.get('focus_areas', ['general']))}
        - Tiempo por sesión: {plan_params.get('session_duration', 45)} minutos
        """
        
        prompt = f"""
        Eres un entrenador personal certificado con 15 años de experiencia. Crea un plan de entrenamiento COMPLETO y DETALLADO.
        
        {user_info}
        {plan_info}
        
        INSTRUCCIONES ESPECÍFICAS:
        1. El plan debe ser progresivo y seguro
        2. Incluye calentamiento y enfriamiento en cada sesión
        3. Varía los ejercicios para evitar monotonía
        4. Ajusta la intensidad según el nivel del usuario
        5. Incluye ejercicios compuestos y de aislamiento
        6. Considera el tiempo de recuperación entre sesiones
        
        FORMATO DE RESPUESTA (JSON estricto):
        {{
            "name": "Nombre atractivo del plan",
            "description": "Descripción motivadora del plan (2-3 líneas)",
            "difficulty": "beginner/intermediate/advanced",
            "estimated_calories_per_session": 300,
            "weeks": [
                {{
                    "week": 1,
                    "focus": "Adaptación y técnica",
                    "workouts": [
                        {{
                            "day": "Lunes",
                            "name": "Tren Superior - Fuerza",
                            "duration_minutes": 45,
                            "warm_up": [
                                {{
                                    "exercise": "Movilidad articular",
                                    "duration": "5 minutos",
                                    "instructions": "Círculos de brazos, rotaciones de hombros"
                                }}
                            ],
                            "main_exercises": [
                                {{
                                    "name": "Press de pecho con mancuernas",
                                    "sets": 3,
                                    "reps": "8-10",
                                    "rest_seconds": 90,
                                    "weight_guidance": "Peso moderado",
                                    "instructions": "Controla el movimiento, baja lentamente",
                                    "muscle_groups": ["pecho", "tríceps", "hombros"],
                                    "difficulty": "intermediate"
                                }}
                            ],
                            "cool_down": [
                                {{
                                    "exercise": "Estiramiento de pecho",
                                    "duration": "30 segundos",
                                    "instructions": "Mantén la posición sin rebotes"
                                }}
                            ]
                        }}
                    ]
                }}
            ],
            "nutrition_tips": [
                "Consume proteína dentro de 30 minutos post-entrenamiento",
                "Mantente hidratado durante toda la sesión"
            ],
            "safety_notes": [
                "Detente si sientes dolor agudo",
                "Calienta siempre antes de entrenar"
            ]
        }}
        
        IMPORTANTE: Responde ÚNICAMENTE con el JSON válido, sin texto adicional.
        """
        
        return prompt
    
    @staticmethod
    def generate_plan(user_data: Dict, plan_params: Dict, api_key: str) -> Dict:
        """Genera un plan de entrenamiento usando OpenAI"""
        try:
            openai.api_key = api_key
            
            prompt = AIWorkoutGenerator.create_workout_prompt(user_data, plan_params)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un entrenador personal experto. Respondes ÚNICAMENTE con JSON válido, sin explicaciones adicionales."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Intentar parsear el JSON
            try:
                plan_data = json.loads(content)
                logger.info("Plan de entrenamiento generado exitosamente")
                return plan_data
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando JSON de OpenAI: {e}")
                return AIWorkoutGenerator.create_fallback_workout_plan(plan_params)
                
        except Exception as e:
            logger.error(f"Error generando plan con OpenAI: {e}")
            return AIWorkoutGenerator.create_fallback_workout_plan(plan_params)
    
    @staticmethod
    def create_fallback_workout_plan(plan_params: Dict) -> Dict:
        """Crea un plan de respaldo si falla la IA"""
        goal = plan_params.get('fitness_goal', 'general_fitness')
        level = plan_params.get('activity_level', 'beginner')
        
        return {
            "name": f"Plan de {goal.replace('_', ' ').title()} - {level.title()}",
            "description": f"Plan personalizado de {plan_params.get('duration_weeks', 4)} semanas para {goal}",
            "difficulty": level,
            "estimated_calories_per_session": 250,
            "weeks": [
                {
                    "week": 1,
                    "focus": "Adaptación inicial",
                    "workouts": [
                        {
                            "day": "Lunes",
                            "name": "Entrenamiento de cuerpo completo",
                            "duration_minutes": 30,
                            "main_exercises": [
                                {
                                    "name": "Sentadillas",
                                    "sets": 3,
                                    "reps": "10-12",
                                    "rest_seconds": 60,
                                    "instructions": "Mantén la espalda recta"
                                },
                                {
                                    "name": "Flexiones",
                                    "sets": 3,
                                    "reps": "8-10",
                                    "rest_seconds": 60,
                                    "instructions": "Modifica en rodillas si es necesario"
                                }
                            ]
                        }
                    ]
                }
            ],
            "nutrition_tips": ["Mantente hidratado", "Come proteína después del entrenamiento"],
            "safety_notes": ["Calienta antes de entrenar", "Escucha a tu cuerpo"]
        }


class AINutritionGenerator:
    """Generador de planes nutricionales con IA"""
    
    @staticmethod
    def create_nutrition_prompt(user_data: Dict, plan_params: Dict) -> str:
        """Crea un prompt optimizado para generar planes nutricionales"""
        
        # Calcular macronutrientes según objetivo
        goal = plan_params.get('goal', 'maintenance')
        calories = plan_params.get('daily_calories', 2000)
        
        if goal == 'weight_loss':
            protein_pct, carbs_pct, fats_pct = 35, 35, 30
        elif goal == 'muscle_gain':
            protein_pct, carbs_pct, fats_pct = 30, 45, 25
        elif goal == 'performance':
            protein_pct, carbs_pct, fats_pct = 25, 50, 25
        else:  # maintenance
            protein_pct, carbs_pct, fats_pct = 25, 45, 30
        
        user_info = f"""
        PERFIL DEL USUARIO:
        - Edad: {user_data.get('age', 'No especificada')} años
        - Peso: {user_data.get('weight', 'No especificado')} kg
        - Altura: {user_data.get('height', 'No especificada')} cm
        - Nivel de actividad: {user_data.get('activity_level', 'moderado')}
        - Objetivo: {goal}
        """
        
        plan_info = f"""
        ESPECIFICACIONES DEL PLAN:
        - Calorías diarias objetivo: {calories}
        - Comidas por día: {plan_params.get('meals_per_day', 3)}
        - Duración: {plan_params.get('duration_weeks', 4)} semanas
        - Restricciones dietéticas: {plan_params.get('dietary_restrictions', 'Ninguna')}
        - Alergias: {plan_params.get('allergies', 'Ninguna')}
        - Distribución de macros: {protein_pct}% proteína, {carbs_pct}% carbohidratos, {fats_pct}% grasas
        """
        
        prompt = f"""
        Eres un nutricionista certificado con especialización en nutrición deportiva. Crea un plan nutricional COMPLETO y BALANCEADO.
        
        {user_info}
        {plan_info}
        
        INSTRUCCIONES ESPECÍFICAS:
        1. El plan debe ser realista y sostenible
        2. Incluye variedad de alimentos para evitar monotonía
        3. Considera el timing de nutrientes para optimizar resultados
        4. Incluye opciones de snacks saludables
        5. Proporciona alternativas para cada comida
        6. Incluye consejos de hidratación
        
        FORMATO DE RESPUESTA (JSON estricto):
        {{
            "name": "Nombre atractivo del plan nutricional",
            "description": "Descripción motivadora (2-3 líneas)",
            "daily_structure": {{
                "total_calories": {calories},
                "macros": {{
                    "protein_grams": {round(calories * protein_pct / 100 / 4, 1)},
                    "carbs_grams": {round(calories * carbs_pct / 100 / 4, 1)},
                    "fats_grams": {round(calories * fats_pct / 100 / 9, 1)}
                }}
            }},
            "daily_meals": [
                {{
                    "name": "Desayuno",
                    "time": "07:30",
                    "calories": 400,
                    "foods": [
                        {{
                            "name": "Avena con frutas del bosque",
                            "quantity": "1 taza (80g avena + 100g frutas)",
                            "calories": 250,
                            "protein": 8,
                            "carbs": 45,
                            "fats": 4,
                            "benefits": "Rica en fibra y antioxidantes"
                        }}
                    ],
                    "alternatives": [
                        "Yogur griego con granola",
                        "Tostadas integrales con aguacate"
                    ],
                    "preparation_tips": "Prepara la avena la noche anterior para ahorrar tiempo"
                }}
            ],
            "weekly_meal_prep": [
                {{
                    "day": "Domingo",
                    "tasks": [
                        "Cocinar proteínas para la semana",
                        "Lavar y cortar vegetales"
                    ]
                }}
            ],
            "hydration_guide": {{
                "daily_water_goal": "2.5-3 litros",
                "timing": [
                    "1 vaso al despertar",
                    "1 vaso antes de cada comida",
                    "Durante y después del ejercicio"
                ]
            }},
            "supplements_suggestions": [
                {{
                    "name": "Proteína en polvo",
                    "when": "Post-entrenamiento",
                    "reason": "Para alcanzar objetivos de proteína",
                    "optional": true
                }}
            ],
            "success_tips": [
                "Planifica tus comidas con anticipación",
                "Escucha las señales de hambre y saciedad de tu cuerpo"
            ]
        }}
        
        IMPORTANTE: Responde ÚNICAMENTE con el JSON válido, sin texto adicional.
        """
        
        return prompt
    
    @staticmethod
    def generate_plan(user_data: Dict, plan_params: Dict, api_key: str) -> Dict:
        """Genera un plan nutricional usando OpenAI"""
        try:
            openai.api_key = api_key
            
            prompt = AINutritionGenerator.create_nutrition_prompt(user_data, plan_params)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un nutricionista experto. Respondes ÚNICAMENTE con JSON válido, sin explicaciones adicionales."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                plan_data = json.loads(content)
                logger.info("Plan nutricional generado exitosamente")
                return plan_data
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando JSON de OpenAI: {e}")
                return AINutritionGenerator.create_fallback_nutrition_plan(plan_params)
                
        except Exception as e:
            logger.error(f"Error generando plan nutricional con OpenAI: {e}")
            return AINutritionGenerator.create_fallback_nutrition_plan(plan_params)
    
    @staticmethod
    def create_fallback_nutrition_plan(plan_params: Dict) -> Dict:
        """Crea un plan nutricional de respaldo"""
        goal = plan_params.get('goal', 'maintenance')
        calories = plan_params.get('daily_calories', 2000)
        
        return {
            "name": f"Plan Nutricional - {goal.replace('_', ' ').title()}",
            "description": f"Plan balanceado de {calories} calorías diarias para {goal}",
            "daily_structure": {
                "total_calories": calories,
                "macros": {
                    "protein_grams": round(calories * 0.25 / 4, 1),
                    "carbs_grams": round(calories * 0.45 / 4, 1),
                    "fats_grams": round(calories * 0.30 / 9, 1)
                }
            },
            "daily_meals": [
                {
                    "name": "Desayuno",
                    "time": "08:00",
                    "calories": round(calories * 0.25),
                    "foods": [
                        {
                            "name": "Desayuno balanceado",
                            "quantity": "1 porción",
                            "calories": round(calories * 0.25),
                            "protein": 15,
                            "carbs": 30,
                            "fats": 10
                        }
                    ]
                }
            ],
            "hydration_guide": {
                "daily_water_goal": "2-3 litros",
                "timing": ["Al despertar", "Antes de comidas", "Durante ejercicio"]
            },
            "success_tips": [
                "Come de forma regular",
                "Incluye variedad de alimentos",
                "Mantente hidratado"
            ]
        }


class AIPersonalTrainer:
    """Asistente personal de fitness con IA"""
    
    @staticmethod
    def get_personalized_advice(user_data: Dict, question: str, api_key: str) -> str:
        """Proporciona consejos personalizados basados en el perfil del usuario"""
        try:
            openai.api_key = api_key
            
            user_context = f"""
            PERFIL DEL USUARIO:
            - Nombre: {user_data.get('name', 'Usuario')}
            - Edad: {user_data.get('age', 'No especificada')}
            - Objetivo: {user_data.get('fitness_goal', 'No especificado')}
            - Nivel: {user_data.get('activity_level', 'No especificado')}
            - Peso: {user_data.get('weight', 'No especificado')} kg
            - Altura: {user_data.get('height', 'No especificada')} cm
            - Restricciones dietéticas: {user_data.get('dietary_restrictions', 'Ninguna')}
            """
            
            system_prompt = f"""
            Eres un entrenador personal y nutricionista experto con 15 años de experiencia. 
            Proporciona consejos personalizados, motivadores y basados en evidencia científica.
            
            {user_context}
            
            INSTRUCCIONES:
            - Sé específico y práctico en tus consejos
            - Mantén un tono motivador y profesional
            - Adapta las recomendaciones al perfil del usuario
            - Si no tienes información suficiente, pide más detalles
            - Incluye consejos de seguridad cuando sea relevante
            - Limita tu respuesta a 200 palabras máximo
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error obteniendo consejo personalizado: {e}")
            return "Lo siento, no puedo procesar tu consulta en este momento. Por favor, intenta más tarde o consulta con un profesional de la salud."


def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """Calcula la tasa metabólica basal usando la fórmula de Mifflin-St Jeor"""
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:  # female
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    return round(bmr, 1)

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Calcula el gasto energético total diario"""
    activity_factors = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    
    factor = activity_factors.get(activity_level, 1.2)
    return round(bmr * factor, 1)

def calculate_macro_distribution(calories: int, goal: str) -> Dict[str, Dict[str, float]]:
    """Calcula la distribución de macronutrientes según el objetivo"""
    distributions = {
        'weight_loss': {'protein': 35, 'carbs': 35, 'fats': 30},
        'muscle_gain': {'protein': 30, 'carbs': 45, 'fats': 25},
        'performance': {'protein': 25, 'carbs': 50, 'fats': 25},
        'maintenance': {'protein': 25, 'carbs': 45, 'fats': 30}
    }
    
    distribution = distributions.get(goal, distributions['maintenance'])
    
    return {
        'protein': {
            'percentage': distribution['protein'],
            'grams': round(calories * distribution['protein'] / 100 / 4, 1),
            'calories': round(calories * distribution['protein'] / 100)
        },
        'carbs': {
            'percentage': distribution['carbs'],
            'grams': round(calories * distribution['carbs'] / 100 / 4, 1),
            'calories': round(calories * distribution['carbs'] / 100)
        },
        'fats': {
            'percentage': distribution['fats'],
            'grams': round(calories * distribution['fats'] / 100 / 9, 1),
            'calories': round(calories * distribution['fats'] / 100)
        }
    }

