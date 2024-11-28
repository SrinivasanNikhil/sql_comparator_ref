from flask import Blueprint, render_template
import mysql.connector

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(500)
def internal_error(error):
    return render_template('errors/error.html', error='Internal Server Error'), 500

@errors_bp.app_errorhandler(mysql.connector.Error)
def handle_db_error(error):
    return render_template('errors/error.html', error='Database Error'), 500
