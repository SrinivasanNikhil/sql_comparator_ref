from flask import Blueprint

bp = Blueprint('comparator', __name__)

from app.comparator import routes
