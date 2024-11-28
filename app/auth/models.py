from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from app.database import db
from flask import current_app

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get_by_username(username):
        try:
            result = db.execute_query(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            )
            if result:
                user_data = result[0]
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash']
                )
            return None
        except Exception as e:
            current_app.logger.error(f"Error in get_by_username: {e}")
            return None

    @staticmethod
    def get_by_id(user_id):
        try:
            result = db.execute_query(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            if result:
                user_data = result[0]
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash']
                )
            return None
        except Exception as e:
            current_app.logger.error(f"Error in get_by_id: {e}")
            return None
