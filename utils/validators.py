import re
from datetime import datetime, date

def validate_email(email):
    """Valida el formato del email"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Valida que la contraseña cumpla con los requisitos mínimos"""
    if not password:
        return False, "La contraseña es requerida"
    
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    # Opcional: validaciones adicionales
    # if not re.search(r'[A-Z]', password):
    #     return False, "La contraseña debe contener al menos una mayúscula"
    
    # if not re.search(r'[0-9]', password):
    #     return False, "La contraseña debe contener al menos un número"
    
    return True, "Contraseña válida"

def validate_age(age):
    """Valida que la edad esté en un rango válido"""
    if age is None:
        return True, "Edad no proporcionada"
    
    try:
        age = int(age)
        if age < 13 or age > 120:
            return False, "La edad debe estar entre 13 y 120 años"
        return True, "Edad válida"
    except (ValueError, TypeError):
        return False, "La edad debe ser un número válido"

def validate_weight(weight):
    """Valida que el peso esté en un rango válido"""
    if weight is None:
        return True, "Peso no proporcionado"
    
    try:
        weight = float(weight)
        if weight < 20 or weight > 500:
            return False, "El peso debe estar entre 20 y 500 kg"
        return True, "Peso válido"
    except (ValueError, TypeError):
        return False, "El peso debe ser un número válido"

def validate_height(height):
    """Valida que la altura esté en un rango válido"""
    if height is None:
        return True, "Altura no proporcionada"
    
    try:
        height = float(height)
        if height < 100 or height > 250:
            return False, "La altura debe estar entre 100 y 250 cm"
        return True, "Altura válida"
    except (ValueError, TypeError):
        return False, "La altura debe ser un número válido"

def validate_body_fat(body_fat):
    """Valida que el porcentaje de grasa corporal esté en un rango válido"""
    if body_fat is None:
        return True, "Grasa corporal no proporcionada"
    
    try:
        body_fat = float(body_fat)
        if body_fat < 3 or body_fat > 50:
            return False, "El porcentaje de grasa corporal debe estar entre 3% y 50%"
        return True, "Grasa corporal válida"
    except (ValueError, TypeError):
        return False, "La grasa corporal debe ser un número válido"

def validate_date(date_string):
    """Valida que la fecha esté en formato correcto"""
    if not date_string:
        return False, "Fecha requerida"
    
    try:
        parsed_date = datetime.strptime(date_string, '%Y-%m-%d').date()
        
        # No permitir fechas futuras
        if parsed_date > date.today():
            return False, "La fecha no puede ser futura"
        
        # No permitir fechas muy antiguas (más de 10 años)
        if (date.today() - parsed_date).days > 3650:
            return False, "La fecha no puede ser anterior a 10 años"
        
        return True, "Fecha válida"
    except ValueError:
        return False, "Formato de fecha inválido. Use YYYY-MM-DD"

def validate_fitness_goal(goal):
    """Valida que el objetivo de fitness sea válido"""
    valid_goals = ['weight_loss', 'muscle_gain', 'endurance', 'strength', 'general_fitness', 'maintenance']
    
    if goal is None:
        return True, "Objetivo no proporcionado"
    
    if goal not in valid_goals:
        return False, f"Objetivo inválido. Debe ser uno de: {', '.join(valid_goals)}"
    
    return True, "Objetivo válido"

def validate_activity_level(level):
    """Valida que el nivel de actividad sea válido"""
    valid_levels = ['beginner', 'intermediate', 'advanced', 'sedentary', 'light', 'moderate', 'active', 'very_active']
    
    if level is None:
        return True, "Nivel de actividad no proporcionado"
    
    if level not in valid_levels:
        return False, f"Nivel de actividad inválido. Debe ser uno de: {', '.join(valid_levels)}"
    
    return True, "Nivel de actividad válido"

def validate_dietary_restrictions(restrictions):
    """Valida las restricciones dietéticas"""
    valid_restrictions = ['none', 'vegetarian', 'vegan', 'keto', 'paleo', 'gluten_free', 'dairy_free', 'low_carb', 'mediterranean']
    
    if restrictions is None or restrictions == '':
        return True, "Restricciones dietéticas no proporcionadas"
    
    if restrictions not in valid_restrictions:
        return False, f"Restricción dietética inválida. Debe ser una de: {', '.join(valid_restrictions)}"
    
    return True, "Restricciones dietéticas válidas"

def validate_subscription_type(sub_type):
    """Valida el tipo de suscripción"""
    valid_types = ['basic', 'premium', 'pro']
    
    if sub_type is None:
        return True, "Tipo de suscripción no proporcionado"
    
    if sub_type not in valid_types:
        return False, f"Tipo de suscripción inválido. Debe ser uno de: {', '.join(valid_types)}"
    
    return True, "Tipo de suscripción válido"

def validate_calories(calories):
    """Valida que las calorías estén en un rango válido"""
    if calories is None:
        return True, "Calorías no proporcionadas"
    
    try:
        calories = int(calories)
        if calories < 800 or calories > 5000:
            return False, "Las calorías deben estar entre 800 y 5000"
        return True, "Calorías válidas"
    except (ValueError, TypeError):
        return False, "Las calorías deben ser un número válido"

def validate_measurement(measurement, field_name, min_val=0, max_val=300):
    """Valida medidas corporales generales"""
    if measurement is None:
        return True, f"{field_name} no proporcionada"
    
    try:
        measurement = float(measurement)
        if measurement < min_val or measurement > max_val:
            return False, f"{field_name} debe estar entre {min_val} y {max_val} cm"
        return True, f"{field_name} válida"
    except (ValueError, TypeError):
        return False, f"{field_name} debe ser un número válido"

def validate_progress_data(data):
    """Valida todos los datos de un registro de progreso"""
    errors = []
    
    # Validar fecha
    if 'date' in data:
        is_valid, message = validate_date(data['date'])
        if not is_valid:
            errors.append(f"Fecha: {message}")
    
    # Validar peso
    if 'weight' in data:
        is_valid, message = validate_weight(data['weight'])
        if not is_valid:
            errors.append(f"Peso: {message}")
    
    # Validar grasa corporal
    if 'body_fat' in data:
        is_valid, message = validate_body_fat(data['body_fat'])
        if not is_valid:
            errors.append(f"Grasa corporal: {message}")
    
    # Validar medidas corporales
    measurements = {
        'chest': 'Pecho',
        'waist': 'Cintura',
        'hips': 'Caderas',
        'arms': 'Brazos',
        'thighs': 'Muslos'
    }
    
    for field, name in measurements.items():
        if field in data:
            is_valid, message = validate_measurement(data[field], name, 20, 200)
            if not is_valid:
                errors.append(f"{name}: {message}")
    
    return len(errors) == 0, errors

def validate_user_profile_data(data):
    """Valida todos los datos del perfil de usuario"""
    errors = []
    
    # Validar email
    if 'email' in data:
        if not validate_email(data['email']):
            errors.append("Email: Formato de email inválido")
    
    # Validar edad
    if 'age' in data:
        is_valid, message = validate_age(data['age'])
        if not is_valid:
            errors.append(f"Edad: {message}")
    
    # Validar peso
    if 'weight' in data:
        is_valid, message = validate_weight(data['weight'])
        if not is_valid:
            errors.append(f"Peso: {message}")
    
    # Validar altura
    if 'height' in data:
        is_valid, message = validate_height(data['height'])
        if not is_valid:
            errors.append(f"Altura: {message}")
    
    # Validar objetivo de fitness
    if 'fitness_goal' in data:
        is_valid, message = validate_fitness_goal(data['fitness_goal'])
        if not is_valid:
            errors.append(f"Objetivo: {message}")
    
    # Validar nivel de actividad
    if 'activity_level' in data:
        is_valid, message = validate_activity_level(data['activity_level'])
        if not is_valid:
            errors.append(f"Nivel de actividad: {message}")
    
    # Validar restricciones dietéticas
    if 'dietary_restrictions' in data:
        is_valid, message = validate_dietary_restrictions(data['dietary_restrictions'])
        if not is_valid:
            errors.append(f"Restricciones dietéticas: {message}")
    
    return len(errors) == 0, errors

