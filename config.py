import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    REFERENCE_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app','reference_files')

    DB_CONFIG = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'database': os.environ.get('DB_NAME')
    }
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'questions')
    #REFERENCE_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'reference_files')
