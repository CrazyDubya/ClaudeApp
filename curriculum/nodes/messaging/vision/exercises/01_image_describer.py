"""
Exercise 1: Image Describer

Goal: Build a tool to describe images using Claude's vision capabilities.

Instructions:
1. Encode an image to base64
2. Send it to Claude with a description prompt
3. Parse and display the response

Challenge:
- Support multiple image formats
- Add different description styles (brief, detailed, technical)
"""

import base64
import os


def encode_image(image_path: str) -> tuple[str, str]:
    """
    TODO: Encode an image file to base64.

    Returns:
        Tuple of (base64_data, media_type)
    """
    import mimetypes

    # Determine media type
    media_type, _ = mimetypes.guess_type(image_path)
    if not media_type or not media_type.startswith("image/"):
        media_type = "image/jpeg"

    # Read and encode
    with open(image_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")

    return data, media_type


def describe_image(
    image_path: str,
    style: str = "medium",
    custom_prompt: str = None,
) -> str:
    """
    TODO: Get a description of an image from Claude.

    Args:
        image_path: Path to the image file
        style: 'brief', 'medium', or 'detailed'
        custom_prompt: Optional custom prompt

    Returns:
        Description of the image
    """
    from anthropic import Anthropic

    client = Anthropic()

    # Encode image
    image_data, media_type = encode_image(image_path)

    # Choose prompt based on style
    prompts = {
        "brief": "Describe this image in one sentence.",
        "medium": "Describe this image in 2-3 sentences, noting the main subjects and setting.",
        "detailed": """Provide a detailed description of this image:
1. Main subjects and their appearance
2. Setting and background
3. Colors, lighting, and mood
4. Any text visible
5. Overall composition""",
    }

    prompt = custom_prompt or prompts.get(style, prompts["medium"])

    # Send request
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    return message.content[0].text


def create_test_image() -> str:
    """Create a simple test image."""
    try:
        from PIL import Image, ImageDraw

        # Create a simple image
        img = Image.new("RGB", (200, 200), color="lightblue")
        draw = ImageDraw.Draw(img)

        # Draw a sun
        draw.ellipse([130, 20, 180, 70], fill="yellow", outline="orange")

        # Draw grass
        draw.rectangle([0, 150, 200, 200], fill="green")

        # Draw a simple house
        draw.rectangle([60, 100, 140, 150], fill="brown", outline="black")
        draw.polygon([(50, 100), (100, 60), (150, 100)], fill="red", outline="black")

        path = "/tmp/test_scene.png"
        img.save(path)
        return path

    except ImportError:
        print("PIL not installed. Run: pip install Pillow")
        return None


def compare_description_styles(image_path: str):
    """Compare different description styles."""
    print("\nComparing description styles:")
    print("=" * 50)

    for style in ["brief", "medium", "detailed"]:
        print(f"\n--- {style.upper()} ---")
        description = describe_image(image_path, style=style)
        print(description)


def main():
    print("=" * 50)
    print("Exercise 1: Image Describer")
    print("=" * 50)

    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("\nValidation mode - skipping API calls")
        print("\nThis exercise demonstrates:")
        print("1. Encoding images to base64")
        print("2. Sending images to Claude")
        print("3. Getting descriptions in different styles")
        return

    # Create a test image
    print("\nCreating test image...")
    image_path = create_test_image()

    if image_path and os.path.exists(image_path):
        print(f"Created: {image_path}")

        # Get a medium description
        print("\nGetting description...")
        description = describe_image(image_path, style="medium")
        print(f"\nDescription:\n{description}")

        # Uncomment to compare all styles:
        # compare_description_styles(image_path)
    else:
        print("\nCould not create test image.")
        print("To use with your own image:")
        print('  describe_image("/path/to/image.jpg")')


if __name__ == "__main__":
    main()
