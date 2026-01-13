"""Main application routes."""

from __future__ import annotations

import threading
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import DogTransformation, User
from app.forms import ImageUploadForm
from app.utils import validate_image, process_image_for_storage
from app.services import generate_dog_transformation

bp = Blueprint('main', __name__)

# Store transformation progress and temporary images in memory
transformation_progress = {}
temporary_images = {}  # Store uploaded images temporarily


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

            # Generate unique token for this upload
            upload_token = secrets.token_urlsafe(32)

            # Store image temporarily in memory with the token
            temporary_images[upload_token] = image_bytes

            # Store token in session (much smaller than the image!)
            session['upload_token'] = upload_token

            flash('Image uploaded successfully! Starting transformation...', 'success')
            return redirect(url_for('main.process'))

        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'danger')
            return render_template('main/upload.html', title='Upload Photo', form=form)

    return render_template('main/upload.html', title='Upload Photo', form=form)


@bp.route('/process')
@login_required
def process() -> str:
    """Display processing page and start transformation in background.

    Returns:
        Rendered processing template
    """
    upload_token = session.get('upload_token')

    if not upload_token or upload_token not in temporary_images:
        flash('No image to process. Please upload an image first.', 'warning')
        return redirect(url_for('main.upload'))

    # Get the image from temporary storage
    image_bytes = temporary_images[upload_token]

    # Initialize progress tracking
    transformation_progress[current_user.id] = {
        'status': 'starting',
        'progress': 0,
        'message': 'Initializing transformation...'
    }

    # Start transformation in background thread
    thread = threading.Thread(
        target=run_transformation,
        args=(current_user.id, image_bytes, upload_token)
    )
    thread.daemon = True
    thread.start()

    return render_template('main/process.html', title='Processing')


def run_transformation(user_id: int, image_bytes: bytes, upload_token: str) -> None:
    """Run the dog transformation in a background thread.

    Args:
        user_id: ID of the user
        image_bytes: Original image bytes
        upload_token: Token for temporary image storage
    """
    from app import create_app
    app = create_app()

    with app.app_context():
        try:
            # Verify user exists
            user = db.session.get(User, user_id)
            if not user:
                raise Exception(f"User with ID {user_id} not found in database")

            # Define progress callback
            def update_progress(progress: int, message: str) -> None:
                """Update the transformation progress."""
                transformation_progress[user_id] = {
                    'status': 'processing',
                    'progress': progress,
                    'message': message
                }

            # Initialize progress
            update_progress(5, 'Starting transformation...')

            # Run the transformation with progress updates
            result = generate_dog_transformation(image_bytes, progress_callback=update_progress)

            # Update progress - saving
            update_progress(85, 'Saving your transformation...')

            # Create transformation object
            transformation = DogTransformation(
                user_id=user_id,
                original_image=image_bytes,
                dog_breed=result['breed'],
                transition_image_1=result['transition_1'],
                transition_image_2=result['transition_2'],
                final_dog_image=result['final_dog']
            )

            db.session.add(transformation)
            db.session.commit()

            # Update progress - complete
            transformation_progress[user_id] = {
                'status': 'complete',
                'progress': 100,
                'message': 'Transformation complete!',
                'transformation_id': transformation.id
            }

            # Clean up temporary image
            temporary_images.pop(upload_token, None)

        except Exception as e:
            # Log the full error for debugging
            import traceback
            print("="*50)
            print("TRANSFORMATION ERROR:")
            print(f"User ID: {user_id}")
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            print("="*50)

            # Update progress - error
            transformation_progress[user_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'Error: {str(e)}'
            }

            # Clean up temporary image
            temporary_images.pop(upload_token, None)


@bp.route('/progress')
@login_required
def progress() -> dict:
    """Get transformation progress via AJAX.

    Returns:
        JSON response with progress data
    """
    progress_data = transformation_progress.get(current_user.id, {
        'status': 'unknown',
        'progress': 0,
        'message': 'No transformation in progress'
    })

    return jsonify(progress_data)


@bp.route('/result/<int:transformation_id>')
@login_required
def result(transformation_id: int) -> str:
    """Display transformation result.

    Args:
        transformation_id: ID of the transformation to display

    Returns:
        Rendered result template
    """
    transformation = db.session.get(DogTransformation, transformation_id)

    if not transformation or transformation.user_id != current_user.id:
        flash('Transformation not found.', 'danger')
        return redirect(url_for('main.gallery'))

    # Clear session data
    session.pop('upload_token', None)

    return render_template(
        'main/result.html',
        title='Your Transformation',
        transformation=transformation
    )


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