"""
Image Describer Example

This example demonstrates how to send images to Claude
for analysis and description.
"""

import base64
import os


def encode_image_to_base64(image_path: str) -> tuple[str, str]:
    """
    Encode an image file to base64.

    Args:
        image_path: Path to the image file

    Returns:
        Tuple of (base64_data, media_type)
    """
    import mimetypes

    # Determine the media type
    media_type, _ = mimetypes.guess_type(image_path)
    if not media_type or not media_type.startswith("image/"):
        # Default to JPEG if unknown
        media_type = "image/jpeg"

    # Read and encode the file
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    return image_data, media_type


def describe_image(image_path: str, detail_level: str = "medium") -> str:
    """
    Get a description of an image from Claude.

    Args:
        image_path: Path to the image file
        detail_level: 'brief', 'medium', or 'detailed'

    Returns:
        Description of the image
    """
    from anthropic import Anthropic

    client = Anthropic()

    # Encode the image
    image_data, media_type = encode_image_to_base64(image_path)

    # Customize prompt based on detail level
    prompts = {
        "brief": "Describe this image in one sentence.",
        "medium": "Describe this image in 2-3 sentences, noting the main subjects and setting.",
        "detailed": """Provide a detailed description of this image including:
1. Main subjects and their appearance
2. Setting and background
3. Colors, lighting, and mood
4. Any text visible in the image
5. Overall composition and style""",
    }

    prompt = prompts.get(detail_level, prompts["medium"])

    # Send to Claude
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
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
    )

    return message.content[0].text


def create_sample_image():
    """Create a simple sample image for testing."""
    try:
        from PIL import Image, ImageDraw

        # Create a simple test image
        img = Image.new("RGB", (200, 200), color="skyblue")
        draw = ImageDraw.Draw(img)

        # Draw a simple shape
        draw.ellipse([50, 50, 150, 150], fill="yellow", outline="orange")

        # Save it
        sample_path = "/tmp/sample_image.png"
        img.save(sample_path)
        return sample_path

    except ImportError:
        print("PIL not installed. Install with: pip install Pillow")
        return None


def main():
    print("Image Describer Example")
    print("=" * 40)

    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("\nValidation mode - showing structure only")
        print("\nThis example demonstrates:")
        print("1. Encoding images to base64")
        print("2. Sending images to Claude")
        print("3. Getting image descriptions")
        print("\nSupported formats: JPEG, PNG, GIF, WebP")
        return

    # Try to create a sample image
    sample_path = create_sample_image()

    if sample_path and os.path.exists(sample_path):
        print(f"\nCreated sample image: {sample_path}")
        print("\nGetting description...")

        description = describe_image(sample_path, detail_level="medium")
        print(f"\nDescription:\n{description}")
    else:
        print("\nTo use this example, provide an image path:")
        print('  describe_image("/path/to/image.jpg")')

        print("\nExample code:")
        print("""
from image_describer import describe_image

# Get a brief description
brief = describe_image("photo.jpg", detail_level="brief")

# Get a detailed analysis
detailed = describe_image("screenshot.png", detail_level="detailed")
""")


if __name__ == "__main__":
    main()
