from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def init_db(app):
    """
    Initializes the database and login manager with the Flask application.
    Creates all database tables if they do not exist.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        SQLAlchemy: The initialized SQLAlchemy object.
    """
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # The tables will be created by the test fixture in conftest.py
    # or by running a 'flask db upgrade' command for production.

    return db
