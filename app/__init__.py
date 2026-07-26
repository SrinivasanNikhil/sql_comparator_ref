import os
from flask import Flask, g, session
from config import Config
from flask_login import LoginManager
from flask_session import Session
from app.database.connection import db

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Flask-Session before other extensions
    Session(app)
    
    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Initialize database
    db.init_app(app)
    
    # Create session directory if it doesn't exist
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REFERENCE_FILES_DIR'], exist_ok=True)

    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.comparator import bp as comparator_bp
    app.register_blueprint(comparator_bp, url_prefix='/')

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.before_request
    def before_request():
        """Set database configuration based on session"""
        # Renew session on each request
        if 'user_id' in session:
            session.modified = True
        
        if 'current_database' in session:
            # Update database configuration with session value
            current_db = session['current_database']
            if current_db in app.config['AVAILABLE_DATABASES']:
                db_name = app.config['AVAILABLE_DATABASES'][current_db]
                app.config['DB_CONFIG'] = app.config['DB_CONFIG'].copy()
                app.config['DB_CONFIG']['database'] = db_name
                
                # Force new database connection
                if hasattr(g, 'db'):
                    delattr(g, 'db')

    @login_manager.user_loader
    def load_user(id):
        from app.auth.models import User
        return User.get_by_id(id)

    return app
