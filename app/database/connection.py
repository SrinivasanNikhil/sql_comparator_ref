import mysql.connector
from mysql.connector import Error
from flask import current_app
from contextlib import contextmanager

class DatabaseConnection:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = mysql.connector.connect(**current_app.config['DB_CONFIG'])
            yield conn
        finally:
            if conn and conn.is_connected():
                conn.close()

    def execute_query(self, query: str, params=None):
        """Execute a query and return results as a list of dictionaries"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                else:
                    conn.commit()
                    results = None
                cursor.close()
                return results
        except Error as e:
            current_app.logger.error(f"Database error: {str(e)}")
            raise

# Create a singleton instance
db = DatabaseConnection()
