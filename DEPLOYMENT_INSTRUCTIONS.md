# 🚀 Instrucciones de Despliegue - Glow-Up AI Backend

## 📋 Configuración de Variables de Entorno

Antes de desplegar, necesitas configurar las siguientes variables de entorno:

### 🔑 Variables Requeridas

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
JWT_SECRET_KEY=tu-jwt-secret-muy-seguro-aqui

# OpenAI Configuration
OPENAI_API_KEY=tu-api-key-de-openai-aqui

# Database Configuration (se configurará automáticamente en Railway)
DATABASE_URL=

# Server Configuration
PORT=5000
```

## 🚂 Despliegue en Railway

### Paso 1: Preparar el repositorio
1. Asegúrate de que el código esté subido a GitHub
2. El archivo `requirements.txt` y `Procfile` ya están incluidos

### Paso 2: Crear proyecto en Railway
1. Ve a [railway.app](https://railway.app)
2. Haz clic en "Start a New Project"
3. Selecciona "Deploy from GitHub repo"
4. Conecta tu repositorio `glow-up-ai-backend`

### Paso 3: Configurar variables de entorno
En el dashboard de Railway, ve a la pestaña "Variables" y agrega:

```
FLASK_ENV=production
SECRET_KEY=glow-up-ai-secret-key-2024-production
JWT_SECRET_KEY=glow-up-ai-jwt-secret-2024-production
OPENAI_API_KEY=tu-api-key-de-openai-aqui
```

**IMPORTANTE:** Reemplaza `tu-api-key-de-openai-aqui` con tu API key real de OpenAI.

### Paso 4: Agregar base de datos
1. En Railway, haz clic en "New" → "Database" → "PostgreSQL"
2. Railway configurará automáticamente la variable `DATABASE_URL`

### Paso 5: Desplegar
1. Railway detectará automáticamente el `Procfile`
2. El despliegue comenzará automáticamente
3. Obtendrás una URL pública para tu API

## 🌐 Despliegue en Heroku (Alternativo)

### Paso 1: Instalar Heroku CLI
```bash
# Instalar Heroku CLI desde https://devcenter.heroku.com/articles/heroku-cli
```

### Paso 2: Crear aplicación
```bash
heroku create tu-app-name-backend
```

### Paso 3: Configurar variables de entorno
```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=glow-up-ai-secret-key-2024-production
heroku config:set JWT_SECRET_KEY=glow-up-ai-jwt-secret-2024-production
heroku config:set OPENAI_API_KEY=tu-api-key-de-openai-aqui
```

### Paso 4: Agregar base de datos
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### Paso 5: Desplegar
```bash
git push heroku main
```

## ✅ Verificar Despliegue

Una vez desplegado, verifica que funcione:

### 1. Health Check
```bash
curl https://tu-app-url.railway.app/api/health
```

Deberías recibir:
```json
{
  "status": "healthy",
  "message": "Glow-Up AI Backend is running!",
  "version": "1.0.0"
}
```

### 2. Test de Registro
```bash
curl -X POST https://tu-app-url.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Test de IA
Una vez registrado y con token, prueba la generación de planes:
```bash
curl -X POST https://tu-app-url.railway.app/api/ai/generate-workout \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tu-jwt-token" \
  -d '{
    "fitness_goal": "muscle_gain",
    "activity_level": "intermediate",
    "duration_weeks": 4,
    "workouts_per_week": 3
  }'
```

## 🔗 Conectar con Frontend

Una vez que tengas la URL del backend desplegado, actualiza la configuración del frontend:

### En el archivo de configuración del frontend:
```javascript
// src/services/api.js
const API_BASE_URL = 'https://tu-app-url.railway.app/api';
```

## 🛠️ Troubleshooting

### Error: "Application Error"
- Verifica que todas las variables de entorno estén configuradas
- Revisa los logs en Railway/Heroku dashboard

### Error: "Database connection failed"
- Asegúrate de que la base de datos PostgreSQL esté creada
- Verifica que la variable `DATABASE_URL` esté configurada

### Error: "OpenAI API Error"
- Verifica que la API key de OpenAI sea válida
- Asegúrate de que tengas créditos disponibles en OpenAI

## 📞 Soporte

Si tienes problemas con el despliegue:
1. Revisa los logs del servicio
2. Verifica que todas las variables estén configuradas
3. Asegúrate de que el repositorio esté actualizado

¡Tu backend está listo para soportar miles de usuarios! 🚀

