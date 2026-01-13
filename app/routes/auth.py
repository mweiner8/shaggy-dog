"""Authentication routes for login, logout, and registration."""

from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register() -> str:
    """Handle user registration.

    Returns:
        Rendered template or redirect response
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            # Log the error in production
            print(f"Registration error: {e}")

    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login() -> str:
    """Handle user login.

    Returns:
        Rendered template or redirect response
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')

            # Redirect to next page if it exists, otherwise go to index
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('auth/login.html', title='Login', form=form)


@bp.route('/logout')
def logout() -> str:
    """Handle user logout.

    Returns:
        Redirect response to login page
    """
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))