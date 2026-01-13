"""Application factory and configuration."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

if TYPE_CHECKING:
    from app.models import User

# Load environment variables
load_dotenv()


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: Configuration to use ('development', 'production', 'testing')

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    from config import config
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # User loader callback
    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        """Load user by ID for Flask-Login.

        Args:
            user_id: String representation of user ID

        Returns:
            User object or None if not found
        """
        from app.models import User
        return db.session.get(User, int(user_id))

    # Register blueprints
    from app.routes import auth, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)

    # Register template filters
    from app.utils import image_bytes_to_base64

    @app.template_filter('b64encode')
    def b64encode_filter(data: bytes) -> str:
        """Convert bytes to base64 string for template display."""
        return image_bytes_to_base64(data)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app