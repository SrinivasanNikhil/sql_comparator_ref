import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    REFERENCE_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'reference_files')

    # Base DB configuration
    DB_CONFIG = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'database': os.environ.get('DB_NAME', 'ClassicModels')  # Default database
    }
    # Available databases mapping
    AVAILABLE_DATABASES = {
        'ClassicModels': 'ClassicModels',  # Changed to lowercase for MySQL compatibility
        'Northwind': 'northwind'  # Changed to match dropdown value
    }
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'questions')
    
    # Session configuration
    SESSION_COOKIE_NAME = 'sql_comparator_session'
    SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protect against CSRF
    PERMANENT_SESSION_LIFETIME = 3600  # Session lifetime in seconds (1 hour)
    SESSION_PROTECTION = 'strong'  # Prevent session hijacking

    # Flask-Session Configuration (update these settings)
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
    SESSION_FILE_THRESHOLD = 500
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 3600
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'sql_comparator:'
    
    # Ensure the session directory exists
    os.makedirs(SESSION_FILE_DIR, exist_ok=True)
