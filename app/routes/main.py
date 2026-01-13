"""Main application routes."""

from __future__ import annotations

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models import DogTransformation
from app.forms import ImageUploadForm
from app.utils import validate_image, process_image_for_storage

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


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload() -> str:
    """Handle image upload for dog transformation.

    Returns:
        Rendered template or redirect response
    """
    form = ImageUploadForm()

    if form.validate_on_submit():
        # Get uploaded file
        file = form.image.data

        # Validate image
        is_valid, error_message = validate_image(file)
        if not is_valid:
            flash(error_message, 'danger')
            return render_template('main/upload.html', title='Upload Photo', form=form)

        try:
            # Process image for storage
            image_bytes = process_image_for_storage(file)

            # Store in session or redirect to processing
            # For now, we'll just show success and redirect
            flash('Image uploaded successfully! Processing will be added in the next stage.', 'success')
            return redirect(url_for('main.index'))

        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'danger')
            return render_template('main/upload.html', title='Upload Photo', form=form)

    return render_template('main/upload.html', title='Upload Photo', form=form)


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