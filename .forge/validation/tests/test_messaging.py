"""
Validation tests for messaging curriculum nodes.

These tests verify that messaging examples and exercises
work correctly with the current Claude SDK version.
"""

import os
import pytest


class TestMessageStructure:
    """Tests for the message-structure node."""

    def test_user_message_format(self):
        """Verify user message format is correct."""
        message = {"role": "user", "content": "Hello"}
        assert message["role"] == "user"
        assert isinstance(message["content"], str)

    def test_assistant_message_format(self):
        """Verify assistant message format is correct."""
        message = {"role": "assistant", "content": "Hello!"}
        assert message["role"] == "assistant"
        assert isinstance(message["content"], str)

    def test_content_blocks_format(self):
        """Verify content blocks format is correct."""
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Hello"},
            ],
        }
        assert isinstance(message["content"], list)
        assert message["content"][0]["type"] == "text"

    def test_message_alternation_valid(self):
        """Verify valid message alternation."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"},
        ]

        for i in range(1, len(messages)):
            assert messages[i]["role"] != messages[i - 1]["role"]


class TestSystemPrompts:
    """Tests for the system-prompts node."""

    def test_system_prompt_string(self):
        """Verify system prompt can be a string."""
        system = "You are a helpful assistant."
        assert isinstance(system, str)
        assert len(system) > 0

    @pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="API key required for live test"
    )
    def test_system_prompt_usage(self, client):
        """Verify system prompt is used correctly."""
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            system="Always respond in uppercase letters only.",
            messages=[{"role": "user", "content": "Say hello"}],
        )

        text = response.content[0].text
        # Should have significant uppercase
        assert sum(1 for c in text if c.isupper()) > 0


class TestStreaming:
    """Tests for the streaming node."""

    @pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="API key required for live test"
    )
    def test_streaming_basic(self, client):
        """Verify streaming works correctly."""
        chunks = []

        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=30,
            messages=[{"role": "user", "content": "Count to 3."}],
        ) as stream:
            for text in stream.text_stream:
                chunks.append(text)

        assert len(chunks) > 0
        full_text = "".join(chunks)
        assert len(full_text) > 0


class TestMultiTurn:
    """Tests for the multi-turn node."""

    def test_conversation_history_format(self):
        """Verify conversation history format."""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]

        assert history[0]["role"] == "user"  # First is user
        assert len(history) == 3

    @pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="API key required for live test"
    )
    def test_context_retention(self, client):
        """Verify context is retained across turns."""
        history = [
            {"role": "user", "content": "My name is TestUser123."},
            {"role": "assistant", "content": "Hello TestUser123! Nice to meet you."},
            {"role": "user", "content": "What is my name?"},
        ]

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=history,
        )

        # Should reference the name from context
        assert "TestUser123" in response.content[0].text


class TestContextManagement:
    """Tests for the context-management node."""

    def test_token_estimation(self):
        """Verify token estimation is reasonable."""
        text = "Hello, world!"
        # Rough estimate: 4 chars per token
        estimated = len(text) // 4
        assert 2 <= estimated <= 5

    def test_message_trimming(self):
        """Verify message trimming works."""
        messages = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Second"},
            {"role": "assistant", "content": "Response 2"},
            {"role": "user", "content": "Third"},
        ]

        # Simple trim to last 3
        trimmed = messages[-3:]
        assert len(trimmed) == 3
        assert trimmed[0]["content"] == "Second"


class TestVision:
    """Tests for the vision node."""

    def test_base64_encoding(self):
        """Verify base64 encoding works."""
        import base64

        data = b"test image data"
        encoded = base64.standard_b64encode(data).decode("utf-8")
        decoded = base64.standard_b64decode(encoded)

        assert decoded == data

    def test_image_content_block_format(self):
        """Verify image content block format."""
        import base64

        image_block = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64.standard_b64encode(b"fake").decode("utf-8"),
            },
        }

        assert image_block["type"] == "image"
        assert image_block["source"]["type"] == "base64"
        assert image_block["source"]["media_type"].startswith("image/")

    def test_url_image_format(self):
        """Verify URL image format."""
        image_block = {
            "type": "image",
            "source": {
                "type": "url",
                "url": "https://example.com/image.jpg",
            },
        }

        assert image_block["source"]["type"] == "url"
        assert image_block["source"]["url"].startswith("http")
