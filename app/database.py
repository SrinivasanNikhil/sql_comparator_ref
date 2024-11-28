import mysql.connector
from mysql.connector import Error
from flask import current_app
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """Context manager for MySQL database connections"""
    conn = None
    try:
        conn = mysql.connector.connect(**current_app.config['DB_CONFIG'])
        yield conn
    except Error as e:
        raise Exception(f"Database connection error: {str(e)}")
    finally:
        if conn and conn.is_connected():
            conn.close()

def dict_fetchall(cursor):
    """Convert MySQL cursor results to dictionary"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
