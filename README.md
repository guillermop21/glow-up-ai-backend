# Glow-Up AI Backend

Backend API para la aplicación Glow-Up AI - Planes personalizados de fitness y nutrición generados con Inteligencia Artificial.

## 🚀 Características Principales

### 🤖 Inteligencia Artificial Integrada
- **Generación de Planes de Entrenamiento**: Planes personalizados basados en objetivos, nivel y equipo disponible
- **Planes Nutricionales Inteligentes**: Dietas balanceadas con cálculo automático de macronutrientes
- **Asistente Personal**: Chat con IA para consejos personalizados de fitness y nutrición
- **Análisis Avanzado**: Insights y recomendaciones basadas en el progreso del usuario

### 📊 Seguimiento Completo
- **Progreso Detallado**: Peso, grasa corporal, masa muscular y medidas corporales
- **Estadísticas Avanzadas**: Tendencias, rachas, promedios y análisis de progreso
- **Objetivos SMART**: Metas personalizadas y seguimiento automático
- **Analytics Inteligentes**: Insights y recomendaciones basadas en datos

### 🔐 Seguridad y Autenticación
- **JWT Authentication**: Tokens seguros con expiración configurable
- **Validación Robusta**: Validación completa de datos de entrada
- **Encriptación de Contraseñas**: Hash seguro con bcrypt
- **Manejo de Errores**: Respuestas consistentes y logging detallado

### 🏗️ Arquitectura Escalable
- **Base de Datos Flexible**: SQLite para desarrollo, PostgreSQL para producción
- **API RESTful**: Endpoints bien estructurados y documentados
- **CORS Configurado**: Soporte para múltiples dominios frontend
- **Optimizado para la Nube**: Listo para despliegue en Railway, Heroku, etc.

## 🛠️ Tecnologías Utilizadas

- **Framework**: Flask 2.3.3
- **Base de Datos**: SQLAlchemy con soporte para SQLite/PostgreSQL
- **Autenticación**: Flask-JWT-Extended
- **IA**: OpenAI GPT-3.5-turbo
- **Validación**: Validadores personalizados
- **CORS**: Flask-CORS
- **Servidor**: Gunicorn para producción

## 📁 Estructura del Proyecto

```
glow-up-backend/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias Python
├── .env                  # Variables de entorno
├── models/
│   └── user.py           # Modelos de datos (User, WorkoutPlan, NutritionPlan, ProgressEntry)
├── routes/
│   ├── auth.py           # Autenticación y registro
│   ├── user.py           # Gestión de usuarios
│   ├── ai_plans.py       # Generación de planes con IA
│   ├── workout_plans.py  # Gestión de planes de entrenamiento
│   ├── nutrition_plans.py # Gestión de planes nutricionales
│   └── progress.py       # Seguimiento de progreso
└── utils/
    ├── validators.py     # Validadores de datos
    └── ai_helpers.py     # Utilidades para IA
```

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/glow-up-ai-backend.git
cd glow-up-ai-backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo `.env` con:
```env
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-aqui
JWT_SECRET_KEY=tu-jwt-secret-aqui
OPENAI_API_KEY=tu-openai-api-key-aqui
DATABASE_URL=sqlite:///glow_up.db
PORT=5000
```

### 5. Ejecutar la aplicación
```bash
python app.py
```

La API estará disponible en `http://localhost:5000`

## 📚 Endpoints de la API

### 🔐 Autenticación
- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Inicio de sesión
- `GET /api/auth/me` - Obtener usuario actual
- `POST /api/auth/refresh` - Renovar token
- `POST /api/auth/change-password` - Cambiar contraseña

### 👤 Usuario
- `GET /api/user/profile` - Obtener perfil
- `PUT /api/user/profile` - Actualizar perfil
- `GET /api/user/stats` - Estadísticas del usuario
- `GET /api/user/subscription` - Estado de suscripción
- `DELETE /api/user/delete` - Eliminar cuenta

### 🤖 IA y Planes
- `POST /api/ai/generate-workout` - Generar plan de entrenamiento
- `POST /api/ai/generate-nutrition` - Generar plan nutricional
- `POST /api/ai/chat` - Chat con asistente IA

### 🏋️ Planes de Entrenamiento
- `GET /api/workouts/` - Listar planes
- `POST /api/workouts/` - Crear plan
- `GET /api/workouts/{id}` - Obtener plan específico
- `PUT /api/workouts/{id}` - Actualizar plan
- `DELETE /api/workouts/{id}` - Eliminar plan
- `POST /api/workouts/{id}/start` - Iniciar plan
- `POST /api/workouts/{id}/complete` - Completar plan
- `POST /api/workouts/{id}/progress` - Actualizar progreso

### 🥗 Planes Nutricionales
- `GET /api/nutrition/` - Listar planes
- `POST /api/nutrition/` - Crear plan
- `GET /api/nutrition/{id}` - Obtener plan específico
- `PUT /api/nutrition/{id}` - Actualizar plan
- `DELETE /api/nutrition/{id}` - Eliminar plan
- `POST /api/nutrition/calculate-calories` - Calcular calorías

### 📈 Progreso
- `GET /api/progress/` - Obtener registros de progreso
- `POST /api/progress/` - Crear registro
- `PUT /api/progress/{id}` - Actualizar registro
- `DELETE /api/progress/{id}` - Eliminar registro
- `GET /api/progress/stats` - Estadísticas de progreso
- `GET /api/progress/analytics` - Análisis avanzado
- `GET /api/progress/goals` - Objetivos personalizados

## 🌟 Características Avanzadas

### Generación Inteligente de Planes
- **Prompts Optimizados**: Prompts específicos para generar planes detallados y personalizados
- **Fallback Inteligente**: Planes de respaldo si falla la conexión con OpenAI
- **Validación de Contenido**: Verificación automática de la calidad de los planes generados

### Analytics de Progreso
- **Tendencias Automáticas**: Cálculo de tendencias en peso, grasa corporal y medidas
- **Insights Personalizados**: Recomendaciones basadas en el progreso individual
- **Objetivos SMART**: Generación automática de objetivos específicos, medibles y alcanzables

### Validación Robusta
- **Validadores Personalizados**: Validación específica para cada tipo de dato
- **Manejo de Errores**: Respuestas consistentes y mensajes de error claros
- **Logging Detallado**: Registro completo para debugging y monitoreo

## 🔧 Configuración para Producción

### Variables de Entorno Requeridas
```env
FLASK_ENV=production
SECRET_KEY=clave-secreta-muy-segura
JWT_SECRET_KEY=jwt-secret-muy-seguro
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://usuario:password@host:puerto/database
PORT=5000
```

### Despliegue en Railway
1. Conecta tu repositorio de GitHub
2. Configura las variables de entorno
3. Railway detectará automáticamente el archivo `requirements.txt`
4. La aplicación se desplegará automáticamente

### Despliegue en Heroku
```bash
heroku create tu-app-name
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=tu-secret-key
heroku config:set JWT_SECRET_KEY=tu-jwt-secret
heroku config:set OPENAI_API_KEY=tu-openai-key
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

## 🧪 Testing

### Ejecutar tests
```bash
python -m pytest tests/
```

### Test de endpoints
```bash
# Verificar que la API esté funcionando
curl http://localhost:5000/api/health

# Registrar usuario de prueba
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
```

## 📝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Soporte

Si tienes alguna pregunta o necesitas ayuda:

- 📧 Email: support@glowup-ai.com
- 💬 Discord: [Servidor de la comunidad](https://discord.gg/glowup-ai)
- 📖 Documentación: [docs.glowup-ai.com](https://docs.glowup-ai.com)

## 🎯 Roadmap

### Próximas Características
- [ ] Integración con wearables (Fitbit, Apple Watch)
- [ ] Planes de entrenamiento con video
- [ ] Comunidad y desafíos
- [ ] Análisis de imágenes corporales con IA
- [ ] Integración con apps de nutrición
- [ ] Notificaciones push inteligentes

---

**Desarrollado con ❤️ para transformar vidas a través del fitness inteligente**

