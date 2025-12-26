# Vision Capabilities

**Category:** Messaging
**Difficulty:** 2/5
**Estimated Time:** 35 minutes
**Prerequisites:** [Message Structure](../message-structure/)

---

## Learning Objectives

By the end of this node, you will:
- Send images to Claude for analysis
- Work with different image formats and sources
- Combine text and image inputs effectively

---

## Concept Overview

Claude can process and understand images as part of conversations. This enables use cases like:
- Image description and analysis
- Document and diagram understanding
- Visual question answering
- UI/screenshot analysis
- Chart and graph interpretation

### Supported Image Formats

| Format | MIME Type | Notes |
|--------|-----------|-------|
| JPEG | `image/jpeg` | Most common, good for photos |
| PNG | `image/png` | Good for screenshots, diagrams |
| GIF | `image/gif` | Static GIFs only |
| WebP | `image/webp` | Modern format, good compression |

### Image Limits

- Maximum size: 20MB per image
- Maximum dimensions: 8192 x 8192 pixels
- Multiple images per message: Supported
- Token cost: Based on image size and detail

---

## Key Patterns

### Base64 Encoded Images

The most common approach - embed the image data directly:

```python
import base64
from anthropic import Anthropic

client = Anthropic()

def encode_image(image_path: str) -> tuple[str, str]:
    """Read and encode an image file to base64."""
    import mimetypes

    # Determine media type
    media_type, _ = mimetypes.guess_type(image_path)
    if not media_type:
        media_type = "image/jpeg"

    # Read and encode
    with open(image_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")

    return data, media_type


def analyze_image(image_path: str, prompt: str) -> str:
    """Send an image to Claude for analysis."""
    image_data, media_type = encode_image(image_path)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
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
```

### URL-Based Images

Reference images by URL (must be publicly accessible):

```python
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": "https://example.com/image.jpg",
                    },
                },
                {
                    "type": "text",
                    "text": "What do you see in this image?",
                },
            ],
        }
    ],
)
```

### Multiple Images

Send multiple images in a single message:

```python
def compare_images(image_paths: list[str], prompt: str) -> str:
    """Send multiple images for comparison."""
    content = []

    for path in image_paths:
        image_data, media_type = encode_image(path)
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data,
            },
        })

    content.append({
        "type": "text",
        "text": prompt,
    })

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": content}],
    )

    return message.content[0].text


# Usage
result = compare_images(
    ["before.png", "after.png"],
    "Compare these two images and describe the differences."
)
```

---

## Use Case Examples

### Document Analysis

```python
def analyze_document(document_image: str) -> dict:
    """Extract information from a document image."""
    response = analyze_image(
        document_image,
        """Analyze this document and extract:
        1. Document type
        2. Key information (dates, names, amounts)
        3. Any important notes or warnings
        Format as structured data."""
    )
    return {"analysis": response}
```

### Screenshot Description

```python
def describe_ui(screenshot_path: str) -> str:
    """Describe a UI screenshot for accessibility or documentation."""
    return analyze_image(
        screenshot_path,
        """Describe this user interface:
        1. What application or website is shown?
        2. What are the main UI elements visible?
        3. What actions appear to be available to the user?"""
    )
```

### Chart Interpretation

```python
def interpret_chart(chart_path: str) -> str:
    """Interpret data from a chart or graph."""
    return analyze_image(
        chart_path,
        """Analyze this chart:
        1. What type of chart is this?
        2. What data is being displayed?
        3. What are the key trends or insights?
        4. Summarize the main takeaways."""
    )
```

---

## Best Practices

### 1. Optimize Image Size

Large images cost more tokens and take longer to process:

```python
from PIL import Image

def resize_for_analysis(image_path: str, max_size: int = 1568) -> str:
    """Resize image to optimize for Claude processing."""
    img = Image.open(image_path)

    # Calculate new dimensions
    ratio = min(max_size / img.width, max_size / img.height)
    if ratio < 1:
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    # Save to temp file
    output_path = f"/tmp/resized_{os.path.basename(image_path)}"
    img.save(output_path, quality=85)
    return output_path
```

### 2. Provide Clear Context

```python
# Less effective
prompt = "What is this?"

# More effective
prompt = """This is a screenshot of our application's settings page.
Please identify:
1. Any usability issues
2. Inconsistencies in the design
3. Suggestions for improvement"""
```

### 3. Handle Image Loading Errors

```python
def safe_analyze_image(image_path: str, prompt: str) -> str:
    """Analyze image with error handling."""
    try:
        if not os.path.exists(image_path):
            return f"Error: Image not found at {image_path}"

        file_size = os.path.getsize(image_path)
        if file_size > 20 * 1024 * 1024:  # 20MB limit
            return "Error: Image exceeds 20MB size limit"

        return analyze_image(image_path, prompt)

    except Exception as e:
        return f"Error processing image: {str(e)}"
```

---

## Common Pitfalls

1. **Wrong media type**: Ensure the media_type matches the actual image format
2. **Base64 encoding errors**: Use `standard_b64encode`, not URL-safe encoding
3. **Oversized images**: Resize large images before sending
4. **Missing text prompt**: Always include a text prompt with your image

---

## Exercises

1. **Image Describer** (`exercises/01_image_describer.py`): Build an image description tool
2. **Document Extractor** (`exercises/02_document_extractor.py`): Extract text from document images
3. **Visual Comparison** (`exercises/03_visual_comparison.py`): Compare before/after images

---

## Next Steps

After completing this node, proceed to:
- [Streaming Responses](../streaming/) - Real-time response handling
- [Tool Basics](../../tools/tool-basics/) - Define tools for Claude to use
