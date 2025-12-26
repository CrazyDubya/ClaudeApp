"""
Exercise 1: Environment Variable Setup

Goal: Learn to properly configure API keys using environment variables.

Instructions:
1. Create a .env file (if using python-dotenv)
2. Set ANTHROPIC_API_KEY in your environment
3. Run this script to verify

Challenge:
- Implement a function that loads the key with proper error handling
- Mask the key for safe display
"""

import os


def load_api_key_basic() -> str:
    """
    TODO: Implement this function to load the API key.

    Requirements:
    - Read from ANTHROPIC_API_KEY environment variable
    - Raise ValueError if not set
    - Return the key string
    """
    # YOUR CODE HERE
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    return key


def mask_api_key(key: str) -> str:
    """
    TODO: Implement this function to mask the API key.

    Requirements:
    - Show first 7 characters
    - Show last 4 characters
    - Hide everything else with "..."

    Example: "sk-ant-...xyz1"
    """
    # YOUR CODE HERE
    if len(key) <= 15:
        return "***"
    return f"{key[:7]}...{key[-4:]}"


def load_with_dotenv() -> str:
    """
    TODO: Load API key using python-dotenv (optional).

    Requirements:
    - Try to import dotenv
    - Load .env file if available
    - Fall back to regular environment variable
    """
    # YOUR CODE HERE
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass  # dotenv not installed, continue with regular env

    return load_api_key_basic()


def test_your_implementation():
    """Run tests on your implementation."""
    print("Testing your implementation...")
    print()

    # Test 1: mask_api_key
    test_key = "sk-ant-api123456789abcdefghijklmnop"
    masked = mask_api_key(test_key)
    print(f"Test 1 - Mask key:")
    print(f"  Input:  {test_key}")
    print(f"  Output: {masked}")
    assert masked.startswith("sk-ant-"), "Should keep first 7 chars"
    assert masked.endswith("mnop"), "Should keep last 4 chars"
    assert "..." in masked, "Should contain ..."
    print("  ✓ Passed")
    print()

    # Test 2: load_api_key_basic
    print("Test 2 - Load API key:")
    try:
        key = load_api_key_basic()
        print(f"  Loaded: {mask_api_key(key)}")
        print("  ✓ Passed")
    except ValueError as e:
        print(f"  Note: {e}")
        print("  Set ANTHROPIC_API_KEY to test this function")
    print()

    print("All tests completed!")


if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 1: Environment Variable Setup")
    print("=" * 50)
    print()
    test_your_implementation()
