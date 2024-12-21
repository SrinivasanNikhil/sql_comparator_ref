import os
from flask import Flask, g
from config import Config
from flask_login import LoginManager
from app.database.connection import db

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REFERENCE_FILES_DIR'], exist_ok=True)

    # Initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Initialize database with app
    db.init_app(app)

    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.comparator import bp as comparator_bp
    app.register_blueprint(comparator_bp, url_prefix='/')

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.before_request
    def before_request():
        """Ensure database configuration is available in application context"""
        if not hasattr(g, 'db_config'):
            g.db_config = app.config['DB_CONFIG']

    @login_manager.user_loader
    def load_user(id):
        from app.auth.models import User
        return User.get_by_id(id)

    return app
