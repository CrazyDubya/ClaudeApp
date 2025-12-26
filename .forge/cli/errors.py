#!/usr/bin/env python3
"""
Claude App Forge - Error Handler

Provides helpful, contextual error messages for common issues.
Wraps SDK exceptions with actionable guidance.

Usage:
    from errors import handle_error, ForgeError

    try:
        # your code
    except Exception as e:
        handle_error(e)
"""

import os
import sys
from dataclasses import dataclass
from typing import Optional


class Colors:
    """ANSI color codes."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    END = "\033[0m"

    @classmethod
    def disable(cls):
        """Disable colors for non-TTY output."""
        cls.GREEN = cls.YELLOW = cls.RED = cls.BLUE = cls.BOLD = cls.END = cls.GRAY = ""


# Disable colors if not a TTY
if not sys.stdout.isatty():
    Colors.disable()


@dataclass
class ErrorInfo:
    """Information about a specific error type."""
    title: str
    description: str
    solutions: list[str]
    docs_link: Optional[str] = None
    example: Optional[str] = None


# Common error patterns and their solutions
ERROR_CATALOG = {
    # Authentication errors
    "authentication_error": ErrorInfo(
        title="Authentication Error",
        description="Your API key is invalid or not set correctly.",
        solutions=[
            "Set the ANTHROPIC_API_KEY environment variable",
            "Check that your API key starts with 'sk-ant-'",
            "Verify your key at https://console.anthropic.com/",
            "Ensure the key hasn't been revoked or expired",
        ],
        docs_link="curriculum/nodes/fundamentals/api-keys/README.md",
        example='export ANTHROPIC_API_KEY="sk-ant-..."',
    ),

    "missing_api_key": ErrorInfo(
        title="Missing API Key",
        description="No API key was provided to the client.",
        solutions=[
            "Set ANTHROPIC_API_KEY environment variable",
            "Or pass api_key parameter to Anthropic()",
            "Run the setup wizard: python .forge/cli/setup_wizard.py",
        ],
        docs_link="curriculum/nodes/fundamentals/api-keys/README.md",
        example='client = Anthropic()  # Uses ANTHROPIC_API_KEY env var',
    ),

    # Rate limiting
    "rate_limit_error": ErrorInfo(
        title="Rate Limit Exceeded",
        description="You've hit the API rate limit.",
        solutions=[
            "Wait a few seconds and retry",
            "Implement exponential backoff",
            "Consider reducing request frequency",
            "Check your usage tier at console.anthropic.com",
        ],
        example="""
import time
for attempt in range(3):
    try:
        response = client.messages.create(...)
        break
    except anthropic.RateLimitError:
        time.sleep(2 ** attempt)
""",
    ),

    # Model errors
    "invalid_model": ErrorInfo(
        title="Invalid Model",
        description="The specified model doesn't exist or you don't have access.",
        solutions=[
            "Use a valid model: claude-sonnet-4-20250514",
            "Check available models in your account",
            "Ensure you have access to the requested model",
        ],
        docs_link="curriculum/nodes/fundamentals/model-selection/README.md",
        example='model="claude-sonnet-4-20250514"',
    ),

    # Message format errors
    "invalid_message_format": ErrorInfo(
        title="Invalid Message Format",
        description="Messages are not in the correct format.",
        solutions=[
            "Messages must be a list of dicts with 'role' and 'content'",
            "Role must be 'user' or 'assistant'",
            "Content must be a string or list of content blocks",
            "First message role should typically be 'user'",
        ],
        docs_link="curriculum/nodes/messaging/message-structure/README.md",
        example="""
messages = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "How are you?"}
]
""",
    ),

    # Token errors
    "context_length_exceeded": ErrorInfo(
        title="Context Length Exceeded",
        description="Your input is too long for the model's context window.",
        solutions=[
            "Reduce the length of your messages",
            "Summarize or truncate older conversation turns",
            "Use a model with a larger context window",
            "Implement context management (sliding window)",
        ],
        docs_link="curriculum/nodes/messaging/context-management/README.md",
        example="""
# Keep only recent messages
MAX_MESSAGES = 20
if len(messages) > MAX_MESSAGES:
    messages = messages[-MAX_MESSAGES:]
""",
    ),

    "max_tokens_too_large": ErrorInfo(
        title="Max Tokens Too Large",
        description="Requested max_tokens exceeds the model's limit.",
        solutions=[
            "Reduce max_tokens value",
            "Claude Sonnet supports up to 8192 output tokens",
            "Leave headroom for input tokens",
        ],
        example='max_tokens=4096  # A reasonable default',
    ),

    # Connection errors
    "connection_error": ErrorInfo(
        title="Connection Error",
        description="Could not connect to the Anthropic API.",
        solutions=[
            "Check your internet connection",
            "Verify api.anthropic.com is accessible",
            "Check for firewall or proxy issues",
            "Retry after a brief wait",
        ],
    ),

    "timeout_error": ErrorInfo(
        title="Request Timeout",
        description="The API request timed out.",
        solutions=[
            "Increase the timeout value",
            "Reduce the complexity of your request",
            "Check for network latency issues",
            "Retry the request",
        ],
        example='client = Anthropic(timeout=60.0)',
    ),

    # SDK installation
    "import_error": ErrorInfo(
        title="SDK Not Installed",
        description="The Anthropic SDK is not installed.",
        solutions=[
            "Install with: pip install anthropic",
            "Check you're in the right virtual environment",
            "Run the setup wizard: python .forge/cli/setup_wizard.py",
        ],
        example="pip install anthropic",
    ),

    # Streaming errors
    "stream_error": ErrorInfo(
        title="Streaming Error",
        description="Error occurred during streaming response.",
        solutions=[
            "Ensure you're properly iterating over the stream",
            "Use 'with' statement for proper cleanup",
            "Handle StreamError exceptions",
        ],
        docs_link="curriculum/nodes/fundamentals/streaming/README.md",
        example="""
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
""",
    ),

    # Tool use errors
    "invalid_tool_definition": ErrorInfo(
        title="Invalid Tool Definition",
        description="Tool definition is malformed.",
        solutions=[
            "Ensure 'name' and 'description' are provided",
            "Input schema must be valid JSON Schema",
            "Check for required properties",
        ],
        example="""
tools = [{
    "name": "get_weather",
    "description": "Get current weather",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}]
""",
    ),

    # Vision errors
    "invalid_image": ErrorInfo(
        title="Invalid Image",
        description="Image could not be processed.",
        solutions=[
            "Ensure image is base64 encoded",
            "Use supported formats: JPEG, PNG, GIF, WebP",
            "Check image size (max 20MB)",
            "Verify media_type matches actual format",
        ],
        docs_link="curriculum/nodes/messaging/vision/README.md",
        example="""
import base64
with open("image.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")
""",
    ),
}


def identify_error(exception: Exception) -> Optional[ErrorInfo]:
    """Identify the error type and return corresponding info."""
    error_str = str(exception).lower()
    error_type = type(exception).__name__.lower()

    # Check for specific exception types
    if "anthropic" in sys.modules:
        import anthropic

        if isinstance(exception, anthropic.AuthenticationError):
            return ERROR_CATALOG["authentication_error"]
        elif isinstance(exception, anthropic.RateLimitError):
            return ERROR_CATALOG["rate_limit_error"]
        elif isinstance(exception, anthropic.APIConnectionError):
            return ERROR_CATALOG["connection_error"]
        elif isinstance(exception, anthropic.APITimeoutError):
            return ERROR_CATALOG["timeout_error"]

    # Check by error message content
    if "api_key" in error_str or "authentication" in error_str:
        if "missing" in error_str or "not provided" in error_str:
            return ERROR_CATALOG["missing_api_key"]
        return ERROR_CATALOG["authentication_error"]

    if "rate limit" in error_str or "rate_limit" in error_str:
        return ERROR_CATALOG["rate_limit_error"]

    if "model" in error_str and ("invalid" in error_str or "not found" in error_str):
        return ERROR_CATALOG["invalid_model"]

    if "context" in error_str and "length" in error_str:
        return ERROR_CATALOG["context_length_exceeded"]

    if "max_tokens" in error_str:
        return ERROR_CATALOG["max_tokens_too_large"]

    if "message" in error_str and ("format" in error_str or "invalid" in error_str):
        return ERROR_CATALOG["invalid_message_format"]

    if isinstance(exception, ImportError) and "anthropic" in error_str:
        return ERROR_CATALOG["import_error"]

    if "timeout" in error_str:
        return ERROR_CATALOG["timeout_error"]

    if "connection" in error_str:
        return ERROR_CATALOG["connection_error"]

    if "stream" in error_str:
        return ERROR_CATALOG["stream_error"]

    if "tool" in error_str and ("invalid" in error_str or "schema" in error_str):
        return ERROR_CATALOG["invalid_tool_definition"]

    if "image" in error_str or "base64" in error_str:
        return ERROR_CATALOG["invalid_image"]

    return None


def format_error(error_info: ErrorInfo, exception: Exception) -> str:
    """Format an error with helpful information."""
    lines = []

    lines.append("")
    lines.append(f"{Colors.RED}{'═' * 60}{Colors.END}")
    lines.append(f"{Colors.RED}{Colors.BOLD}ERROR: {error_info.title}{Colors.END}")
    lines.append(f"{Colors.RED}{'═' * 60}{Colors.END}")
    lines.append("")
    lines.append(f"{Colors.BOLD}What happened:{Colors.END}")
    lines.append(f"  {error_info.description}")
    lines.append("")
    lines.append(f"{Colors.GRAY}Original error: {str(exception)[:100]}{Colors.END}")
    lines.append("")

    lines.append(f"{Colors.BOLD}How to fix:{Colors.END}")
    for i, solution in enumerate(error_info.solutions, 1):
        lines.append(f"  {i}. {solution}")
    lines.append("")

    if error_info.example:
        lines.append(f"{Colors.BOLD}Example:{Colors.END}")
        for line in error_info.example.strip().split("\n"):
            lines.append(f"  {Colors.BLUE}{line}{Colors.END}")
        lines.append("")

    if error_info.docs_link:
        lines.append(f"{Colors.BOLD}Learn more:{Colors.END}")
        lines.append(f"  📚 {error_info.docs_link}")
        lines.append("")

    lines.append(f"{Colors.GRAY}Need more help? Run: python .forge/cli/setup_wizard.py --check{Colors.END}")
    lines.append("")

    return "\n".join(lines)


def handle_error(exception: Exception, exit_on_error: bool = True):
    """Handle an error with helpful output.

    Args:
        exception: The exception to handle
        exit_on_error: Whether to exit after handling (default True)
    """
    error_info = identify_error(exception)

    if error_info:
        print(format_error(error_info, exception), file=sys.stderr)
    else:
        # Generic error handling
        print(f"\n{Colors.RED}Error: {exception}{Colors.END}\n", file=sys.stderr)
        print(f"{Colors.GRAY}This error wasn't recognized. Check:{Colors.END}", file=sys.stderr)
        print("  • Your code syntax and imports", file=sys.stderr)
        print("  • API documentation at docs.anthropic.com", file=sys.stderr)
        print("  • Curriculum examples in curriculum/nodes/", file=sys.stderr)
        print("", file=sys.stderr)

    if exit_on_error:
        sys.exit(1)


class ForgeError(Exception):
    """Base exception for Claude App Forge errors."""
    pass


class ConfigError(ForgeError):
    """Configuration-related error."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        self.suggestion = suggestion
        super().__init__(message)


class ValidationError(ForgeError):
    """Validation-related error."""
    pass


def wrap_sdk_call(func):
    """Decorator to wrap SDK calls with error handling.

    Usage:
        @wrap_sdk_call
        def my_function():
            response = client.messages.create(...)
            return response
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            handle_error(e)
    return wrapper


# Quick error helpers
def check_api_key():
    """Check if API key is set and provide help if not."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        error_info = ERROR_CATALOG["missing_api_key"]
        print(format_error(error_info, ValueError("API key not set")), file=sys.stderr)
        return False

    if not key.startswith("sk-ant-"):
        print(f"{Colors.YELLOW}⚠ Warning: API key doesn't start with 'sk-ant-'{Colors.END}")
        print(f"  This may not be a valid Anthropic API key")
        print()

    return True


def check_sdk_installed():
    """Check if Anthropic SDK is installed."""
    try:
        import anthropic
        return True
    except ImportError:
        error_info = ERROR_CATALOG["import_error"]
        print(format_error(error_info, ImportError("anthropic")), file=sys.stderr)
        return False


def main():
    """Demonstrate error handling."""
    print(f"{Colors.BOLD}Claude App Forge - Error Handler Demo{Colors.END}")
    print("=" * 50)
    print()

    print("Checking prerequisites...")
    print()

    sdk_ok = check_sdk_installed()
    if sdk_ok:
        print(f"  {Colors.GREEN}✓{Colors.END} Anthropic SDK installed")

    api_ok = check_api_key()
    if api_ok:
        print(f"  {Colors.GREEN}✓{Colors.END} API key configured")

    print()
    print("Available error types:")
    for key in ERROR_CATALOG:
        info = ERROR_CATALOG[key]
        print(f"  • {info.title}")

    print()
    print(f"Import in your code: {Colors.BLUE}from .forge.cli.errors import handle_error{Colors.END}")
    print()


if __name__ == "__main__":
    main()
