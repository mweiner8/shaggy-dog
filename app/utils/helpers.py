"""Utility helper functions."""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

from PIL import Image
from werkzeug.datastructures import FileStorage

if TYPE_CHECKING:
    from werkzeug.datastructures import FileStorage


def validate_image(file: FileStorage) -> tuple[bool, str]:
    """Validate uploaded image file.

    Args:
        file: Uploaded file from form

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"

    # Check file size (16MB max)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning

    if file_size > 16 * 1024 * 1024:  # 16MB
        return False, "File size must be less than 16MB"

    # Try to open as image
    try:
        image = Image.open(file.stream)
        image.verify()  # Verify it's a valid image
        file.stream.seek(0)  # Reset stream

        # Check image dimensions
        image = Image.open(file.stream)
        width, height = image.size

        if width < 256 or height < 256:
            return False, "Image must be at least 256x256 pixels"

        if width > 4096 or height > 4096:
            return False, "Image must be less than 4096x4096 pixels"

        file.stream.seek(0)  # Reset stream again
        return True, ""

    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


def process_image_for_storage(file: FileStorage) -> bytes:
    """Process and compress image for database storage.

    Args:
        file: Uploaded file from form

    Returns:
        Compressed image as bytes
    """
    # Open image
    image = Image.open(file.stream)

    # Convert to RGB if needed (for PNG with transparency)
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
        image = background

    # Resize if too large (max 1024x1024 for storage)
    max_size = 1024
    if image.width > max_size or image.height > max_size:
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    # Save to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
    img_byte_arr.seek(0)

    return img_byte_arr.getvalue()


def image_bytes_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string for display.

    Args:
        image_bytes: Image data as bytes

    Returns:
        Base64 encoded string
    """
    import base64
    return base64.b64encode(image_bytes).decode('utf-8')