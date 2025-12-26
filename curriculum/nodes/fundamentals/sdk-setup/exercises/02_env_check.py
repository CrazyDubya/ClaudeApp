"""
Exercise 2: Environment Check

Goal: Verify your environment is properly configured for Claude development.

Instructions:
1. Set your ANTHROPIC_API_KEY environment variable
2. Run this script to verify the configuration
3. Fix any issues identified

Success Criteria:
- API key environment variable is set
- Key format appears valid
- Client can be instantiated
"""

import os
import sys


def check_api_key_set():
    """Check if the API key environment variable exists."""
    print("Checking API key configuration...")

    key = os.environ.get("ANTHROPIC_API_KEY")

    if not key:
        print("  ❌ ANTHROPIC_API_KEY not set")
        print("\n  To set it, run:")
        print('  export ANTHROPIC_API_KEY="your-key-here"')
        return False, None

    print("  ✓ ANTHROPIC_API_KEY is set")
    return True, key


def check_key_format(key: str):
    """Check if the API key has the expected format."""
    print("\nValidating key format...")

    if not key.startswith("sk-ant-"):
        print("  ⚠ Key doesn't start with 'sk-ant-'")
        print("  This may not be a valid Anthropic API key")
        return False

    if len(key) < 20:
        print("  ⚠ Key appears too short")
        return False

    # Mask key for display
    masked = f"{key[:7]}...{key[-4:]}"
    print(f"  ✓ Key format looks valid: {masked}")
    return True


def check_client_creation():
    """Try to create an Anthropic client."""
    print("\nTesting client creation...")

    try:
        from anthropic import Anthropic

        client = Anthropic()
        print("  ✓ Client created successfully")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create client: {e}")
        return False


def main():
    print("=" * 50)
    print("Exercise 2: Environment Check")
    print("=" * 50)
    print()

    key_set, key = check_api_key_set()
    if not key_set:
        sys.exit(1)

    format_ok = check_key_format(key)
    client_ok = check_client_creation()

    print("\n" + "=" * 50)
    if key_set and format_ok and client_ok:
        print("✓ Environment is properly configured!")
    else:
        print("✗ Please fix the issues above.")
    print("=" * 50)


if __name__ == "__main__":
    main()
