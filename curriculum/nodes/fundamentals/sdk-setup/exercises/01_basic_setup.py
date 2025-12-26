"""
Exercise 1: Basic SDK Setup

Goal: Verify your Python environment and install the Anthropic SDK.

Instructions:
1. Run this script to check your Python version
2. Install the SDK if needed: pip install anthropic
3. Verify the installation by running this script again

Success Criteria:
- Python 3.8 or higher
- anthropic package installed
- Script completes without errors
"""

import sys


def check_python_version():
    """Check if Python version meets requirements."""
    print("Checking Python version...")
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ❌ Python 3.8+ required")
        return False

    print("  ✓ Python version OK")
    return True


def check_sdk_installed():
    """Check if the Anthropic SDK is installed."""
    print("\nChecking Anthropic SDK...")
    try:
        import anthropic

        print(f"  ✓ anthropic {anthropic.__version__} installed")
        return True
    except ImportError:
        print("  ❌ anthropic package not found")
        print("  Run: pip install anthropic")
        return False


def check_optional_dependencies():
    """Check for optional but useful packages."""
    print("\nChecking optional dependencies...")

    optional = [
        ("python-dotenv", "dotenv", "Environment file loading"),
        ("httpx", "httpx", "HTTP client (used by SDK)"),
    ]

    for package_name, import_name, description in optional:
        try:
            __import__(import_name)
            print(f"  ✓ {package_name} - {description}")
        except ImportError:
            print(f"  ○ {package_name} - {description} (optional)")


def main():
    print("=" * 50)
    print("Exercise 1: Basic SDK Setup")
    print("=" * 50)
    print()

    python_ok = check_python_version()
    sdk_ok = check_sdk_installed()
    check_optional_dependencies()

    print("\n" + "=" * 50)
    if python_ok and sdk_ok:
        print("✓ Setup complete! You're ready to use the Claude SDK.")
    else:
        print("✗ Setup incomplete. Please fix the issues above.")
    print("=" * 50)


if __name__ == "__main__":
    main()
