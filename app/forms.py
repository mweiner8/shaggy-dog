"""WTForms for user input validation."""

from __future__ import annotations

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
    Regexp
)

from app.models import User


class RegistrationForm(FlaskForm):
    """User registration form.

    Attributes:
        username: Username field (3-80 chars, alphanumeric + underscore)
        email: Email field with validation
        password: Password field (min 8 chars)
        confirm_password: Password confirmation field
        submit: Submit button
    """

    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required.'),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters.'),
            Regexp(
                r'^\w+$',
                message='Username must contain only letters, numbers, and underscores.'
            )
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Please enter a valid email address.'),
            Length(max=120, message='Email must be less than 120 characters.')
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(min=8, message='Password must be at least 8 characters long.')
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password.'),
            EqualTo('password', message='Passwords must match.')
        ]
    )

    submit = SubmitField('Register')

    def validate_username(self, username: StringField) -> None:
        """Check if username already exists.

        Args:
            username: Username field to validate

        Raises:
            ValidationError: If username is already taken
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email: StringField) -> None:
        """Check if email already exists.

        Args:
            email: Email field to validate

        Raises:
            ValidationError: If email is already registered
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class LoginForm(FlaskForm):
    """User login form.

    Attributes:
        username: Username field
        password: Password field
        submit: Submit button
    """

    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required.')
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.')
        ]
    )

    submit = SubmitField('Login')


class ImageUploadForm(FlaskForm):
    """Image upload form for headshot photos.

    Attributes:
        image: File upload field with image validation
        submit: Submit button
    """

    image = FileField(
        'Upload Headshot',
        validators=[
            FileRequired(message='Please select an image file.'),
            FileAllowed(
                ['jpg', 'jpeg', 'png', 'webp'],
                message='Only JPG, PNG, and WebP images are allowed.'
            )
        ]
    )

    submit = SubmitField('Transform to Dog!')