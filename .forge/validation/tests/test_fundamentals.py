"""
Validation tests for fundamentals curriculum nodes.

These tests verify that examples and exercises work correctly
with the current Claude SDK version.
"""

import os
import sys
import pytest


class TestSdkSetup:
    """Tests for the sdk-setup node."""

    def test_sdk_import(self):
        """Verify the SDK can be imported."""
        import anthropic
        assert anthropic is not None

    def test_sdk_version(self):
        """Verify SDK version is accessible."""
        import anthropic
        assert hasattr(anthropic, "__version__")
        assert isinstance(anthropic.__version__, str)

    def test_client_creation_without_key(self, validation_mode):
        """Verify client behavior without API key."""
        import anthropic

        # Temporarily remove API key
        original_key = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            with pytest.raises(anthropic.AuthenticationError):
                client = anthropic.Anthropic()
                # Force authentication check
                client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "test"}],
                )
        finally:
            if original_key:
                os.environ["ANTHROPIC_API_KEY"] = original_key


class TestApiKeys:
    """Tests for the api-keys node."""

    def test_key_loading_example(self, validation_mode):
        """Verify the secure key loading example runs."""
        # Import and run the example in validation mode
        example_path = "curriculum/nodes/fundamentals/api-keys/examples"
        sys.path.insert(0, example_path)
        try:
            from secure_key_loading import mask_key

            # Test key masking
            test_key = "sk-ant-abcdefghijklmnop"
            masked = mask_key(test_key)
            assert masked.startswith("sk-ant-")
            assert "..." in masked
        finally:
            sys.path.pop(0)

    def test_environment_variable_access(self):
        """Verify environment variable access patterns work."""
        # Test os.environ.get pattern
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        assert isinstance(key, str)


class TestFirstMessage:
    """Tests for the first-message node."""

    def test_message_structure(self):
        """Verify message structure is correct."""
        message = {"role": "user", "content": "Hello"}
        assert message["role"] in ["user", "assistant"]
        assert isinstance(message["content"], str)

    @pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="API key required for live test"
    )
    def test_simple_message(self, client):
        """Verify a simple message can be sent."""
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'hello' and nothing else."}],
        )

        assert response.content
        assert len(response.content) > 0
        assert response.content[0].type == "text"
        assert response.stop_reason in ["end_turn", "max_tokens"]


class TestModelSelection:
    """Tests for the model-selection node."""

    def test_model_ids_valid(self):
        """Verify model IDs are correctly formatted."""
        models = [
            "claude-3-5-haiku-20241022",
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
        ]

        for model in models:
            assert "claude" in model
            assert "-" in model

    @pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="API key required for live test"
    )
    def test_haiku_response(self, client):
        """Verify Haiku model responds correctly."""
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=30,
            messages=[{"role": "user", "content": "Say 'test' only."}],
        )

        assert response.model == "claude-3-5-haiku-20241022"
        assert response.content[0].text
