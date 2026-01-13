"""Database models for the application."""

from __future__ import annotations

from datetime import datetime, timezone

import bcrypt
from flask_login import UserMixin
from sqlalchemy import String, Text, LargeBinary, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class User(UserMixin, db.Model):
    """User model for authentication and authorization.

    Attributes:
        id: Primary key
        username: Unique username
        email: Unique email address
        password_hash: Bcrypt hashed password
        created_at: Account creation timestamp
        transformations: Relationship to user's dog transformations
    """

    __tablename__ = 'dog_users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password_hash: Mapped[bytes] = mapped_column(LargeBinary(60), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    transformations: Mapped[list['DogTransformation']] = relationship(
        'DogTransformation',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    def set_password(self, password: str) -> None:
        """Hash and set the user's password.

        Args:
            password: Plain text password to hash
        """
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash.

        Args:
            password: Plain text password to check

        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)

    def __repr__(self) -> str:
        """String representation of User."""
        return f'<User {self.username}>'


class DogTransformation(db.Model):
    """Dog transformation model storing generated images.

    Attributes:
        id: Primary key
        user_id: Foreign key to user
        original_image: Original human headshot (binary)
        dog_breed: Identified dog breed
        transition_image_1: First transition image (binary)
        transition_image_2: Second transition image (binary)
        final_dog_image: Final dog transformation (binary)
        created_at: Transformation creation timestamp
        user: Relationship to user
    """

    __tablename__ = 'dog_transformations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('dog_users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    original_image: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    dog_breed: Mapped[str] = mapped_column(String(100), nullable=False)
    transition_image_1: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    transition_image_2: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    final_dog_image: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships - explicitly reference the User class
    user: Mapped['User'] = relationship(
        'User',
        back_populates='transformations',
        foreign_keys=[user_id]
    )

    def __repr__(self) -> str:
        """String representation of DogTransformation."""
        return f'<DogTransformation {self.id} - {self.dog_breed}>'