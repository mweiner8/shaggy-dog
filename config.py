"""Application configuration."""

from __future__ import annotations

import os
from typing import Final


class Config:
    """Base configuration class."""

    # Flask
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI: str = os.getenv('DATABASE_URL', 'sqlite:///shaggydog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict[str, int | bool] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # OpenAI
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')

    # Upload settings
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS: Final[set[str]] = {'png', 'jpg', 'jpeg', 'webp'}

    # Image generation settings
    TRANSITION_IMAGES_COUNT: int = 2  # Number of transition images between human and dog


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG: bool = True
    TESTING: bool = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG: bool = False
    TESTING: bool = False


class TestingConfig(Config):
    """Testing configuration."""

    DEBUG: bool = True
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///:memory:'


# Configuration dictionary
config: dict[str, type[Config]] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}