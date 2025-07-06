import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar extensiones
db = SQLAlchemy()
jwt = JWTManager()

# Crear la aplicación Flask directamente
app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')

# Configuración de base de datos
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Para Railway/Heroku que usan postgres://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Base de datos local SQLite para desarrollo
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///glow_up.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de OpenAI
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# Inicializar extensiones
db.init_app(app)
jwt.init_app(app)

# Configurar CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Importar y registrar blueprints
from routes.auth import auth_bp
from routes.user import user_bp
from routes.workout_plans import workout_bp
from routes.nutrition_plans import nutrition_bp
from routes.progress import progress_bp
from routes.ai_plans import ai_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(workout_bp, url_prefix='/api/workouts')
app.register_blueprint(nutrition_bp, url_prefix='/api/nutrition')
app.register_blueprint(progress_bp, url_prefix='/api/progress')
app.register_blueprint(ai_bp, url_prefix='/api/ai')

# Crear tablas
with app.app_context():
    db.create_all()

# Ruta de salud
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Glow-Up AI Backend is running!',
        'version': '1.0.0'
    })

# Ruta raíz
@app.route('/')
def index():
    return jsonify({
        'message': 'Glow-Up AI Backend API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'auth': '/api/auth',
            'user': '/api/user',
            'workouts': '/api/workouts',
            'nutrition': '/api/nutrition',
            'progress': '/api/progress',
            'ai': '/api/ai'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
