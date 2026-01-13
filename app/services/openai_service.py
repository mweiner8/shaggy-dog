"""OpenAI API integration for dog breed identification and image generation."""

from __future__ import annotations

import base64
import os
from typing import TYPE_CHECKING

from openai import OpenAI

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletion
    from openai.types import ImagesResponse

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def identify_dog_breed(image_bytes: bytes) -> str:
    """Identify which dog breed most closely resembles a human face.

    Uses GPT-4o-mini with vision to analyze the facial features and
    determine the most similar dog breed.

    Args:
        image_bytes: Image data as bytes

    Returns:
        Name of the identified dog breed

    Raises:
        Exception: If API call fails
    """
    # Encode image to base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    try:
        # Call OpenAI Vision API (using cheaper GPT-4o-mini)
        response: ChatCompletion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert at analyzing human facial features and matching them "
                        "to dog breeds. Analyze the face shape, facial structure, expression, "
                        "and overall appearance to determine which dog breed they most resemble. "
                        "Respond with ONLY the dog breed name, nothing else. Be specific (e.g., "
                        "'Golden Retriever' not just 'Retriever'). Choose popular, recognizable breeds."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What dog breed does this person most closely resemble?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "low"  # Use low detail to reduce cost
                            }
                        }
                    ]
                }
            ],
            max_tokens=50,
            temperature=0.7
        )

        # Extract breed name
        breed = response.choices[0].message.content.strip()
        return breed

    except Exception as e:
        raise Exception(f"Failed to identify dog breed: {str(e)}")


def generate_dog_image(breed: str, transition_stage: str) -> bytes:
    """Generate a dog image for a specific transformation stage.

    Args:
        breed: Name of the dog breed
        transition_stage: Description of the transformation stage

    Returns:
        Generated image as bytes

    Raises:
        Exception: If image generation fails
    """
    try:
        # Create prompt for the specific transition stage
        prompt = (
            f"A photorealistic portrait of a {breed} dog, {transition_stage}. "
            f"Studio lighting, high detail, professional photography, "
            f"centered composition, neutral background."
        )

        # Generate image using DALL-E 3
        response: ImagesResponse = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",  # Use standard quality to reduce cost
            n=1
        )

        # Get image URL
        image_url = response.data[0].url

        # Download the image
        import requests
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        return image_response.content

    except Exception as e:
        raise Exception(f"Failed to generate dog image: {str(e)}")


def generate_transition_image(
    original_image_bytes: bytes,
    breed: str,
    transition_level: float
) -> bytes:
    """Generate a transition image between human and dog.

    Args:
        original_image_bytes: Original human photo
        breed: Dog breed to transform into
        transition_level: How far along the transformation (0.0 to 1.0)

    Returns:
        Generated transition image as bytes

    Raises:
        Exception: If image generation fails
    """
    # Encode original image
    base64_image = base64.b64encode(original_image_bytes).decode('utf-8')

    try:
        # First, use vision to describe the original image
        description_response: ChatCompletion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert at describing human portraits. Describe this person's "
                        "appearance in detail, focusing on face shape, expression, pose, and "
                        "general appearance. Keep it concise but detailed."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this person's appearance:"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "low"
                            }
                        }
                    ]
                }
            ],
            max_tokens=150
        )

        person_description = description_response.choices[0].message.content.strip()

        # Create transition prompt based on level
        if transition_level < 0.5:
            # More human-like
            transformation_desc = (
                f"a portrait that is mostly human but with subtle {breed} dog features beginning to emerge. "
                f"The face is primarily human-like with hints of dog characteristics. "
                f"Based on: {person_description}"
            )
        else:
            # More dog-like
            transformation_desc = (
                f"a portrait that is mostly {breed} dog but retains some human characteristics. "
                f"The face is primarily dog-like but maintains hints of the original human features. "
                f"Based on: {person_description}"
            )

        # Generate the transition image
        prompt = (
            f"A photorealistic portrait showing {transformation_desc}. "
            f"Studio lighting, high detail, professional photography, "
            f"centered composition, neutral background. The transformation should look natural and seamless."
        )

        response: ImagesResponse = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        # Download the image
        import requests
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        return image_response.content

    except Exception as e:
        raise Exception(f"Failed to generate transition image: {str(e)}")


def generate_dog_transformation(
    image_bytes: bytes,
    progress_callback: callable = None
) -> dict[str, bytes | str]:
    """Complete dog transformation pipeline.

    This is the main function that orchestrates the entire transformation:
    1. Identifies the matching dog breed
    2. Generates transition image 1 (33% transformed)
    3. Generates transition image 2 (66% transformed)
    4. Generates final dog image (100% transformed)

    Args:
        image_bytes: Original human headshot as bytes
        progress_callback: Optional function to call with progress updates

    Returns:
        Dictionary with keys:
            - breed: Name of identified dog breed
            - transition_1: First transition image bytes
            - transition_2: Second transition image bytes
            - final_dog: Final dog image bytes

    Raises:
        Exception: If any step of the transformation fails
    """
    try:
        # Step 1: Identify dog breed (10-20%)
        if progress_callback:
            progress_callback(10, "Identifying dog breed...")
        print("Identifying dog breed...")
        breed = identify_dog_breed(image_bytes)
        print(f"Identified breed: {breed}")

        # Step 2: Generate first transition (20-40%)
        if progress_callback:
            progress_callback(20, f"Generating first transition to {breed}...")
        print("Generating transition 1...")
        transition_1 = generate_transition_image(image_bytes, breed, 0.33)

        # Step 3: Generate second transition (40-60%)
        if progress_callback:
            progress_callback(40, f"Generating second transition to {breed}...")
        print("Generating transition 2...")
        transition_2 = generate_transition_image(image_bytes, breed, 0.66)

        # Step 4: Generate final dog image (60-80%)
        if progress_callback:
            progress_callback(60, f"Generating final {breed} image...")
        print("Generating final dog image...")
        final_dog = generate_dog_image(
            breed,
            "facing forward, friendly expression, full portrait"
        )

        if progress_callback:
            progress_callback(80, "Almost done...")

        return {
            'breed': breed,
            'transition_1': transition_1,
            'transition_2': transition_2,
            'final_dog': final_dog
        }

    except Exception as e:
        raise Exception(f"Dog transformation failed: {str(e)}")