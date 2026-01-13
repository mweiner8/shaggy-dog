"""Main application routes."""

from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models import DogTransformation

bp = Blueprint('main', __name__)


@bp.route('/')
@bp.route('/index')
@login_required
def index() -> str:
    """Render the main index/dashboard page.

    Returns:
        Rendered template
    """
    return render_template('main/index.html', title='Dashboard')


@bp.route('/gallery')
@login_required
def gallery() -> str:
    """Display user's dog transformation gallery.

    Returns:
        Rendered template with user's transformations
    """
    transformations = (
        current_user.transformations
        .order_by(DogTransformation.created_at.desc())
        .all()
    )

    return render_template(
        'main/gallery.html',
        title='My Gallery',
        transformations=transformations
    )