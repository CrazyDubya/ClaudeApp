"""
Message Builder Example

This example demonstrates how to build and structure messages
for the Claude API.
"""

import os


class ConversationBuilder:
    """Helper class for building conversation message arrays."""

    def __init__(self):
        self.messages = []

    def add_user_message(self, content: str) -> "ConversationBuilder":
        """Add a user message to the conversation."""
        self.messages.append({"role": "user", "content": content})
        return self

    def add_assistant_message(self, content: str) -> "ConversationBuilder":
        """Add an assistant message to the conversation."""
        self.messages.append({"role": "assistant", "content": content})
        return self

    def get_messages(self) -> list[dict]:
        """Get the built message array."""
        return self.messages

    def validate(self) -> bool:
        """Validate the message structure."""
        if not self.messages:
            print("Error: No messages")
            return False

        if self.messages[0]["role"] != "user":
            print("Error: First message must be from user")
            return False

        for i in range(1, len(self.messages)):
            if self.messages[i]["role"] == self.messages[i - 1]["role"]:
                print(f"Error: Messages must alternate roles (position {i})")
                return False

        return True


def demonstrate_message_structure():
    """Demonstrate proper message structure."""
    print("Message Structure Demonstration")
    print("=" * 40)

    # Build a conversation
    builder = ConversationBuilder()
    builder.add_user_message("What is Python?")
    builder.add_assistant_message(
        "Python is a high-level programming language known for its readability."
    )
    builder.add_user_message("What are its main uses?")

    messages = builder.get_messages()

    print("\nBuilt conversation:")
    for i, msg in enumerate(messages):
        print(f"  {i + 1}. [{msg['role']}]: {msg['content'][:50]}...")

    print(f"\nValidation: {'Passed' if builder.validate() else 'Failed'}")

    return messages


def demonstrate_api_call(messages: list[dict]):
    """Demonstrate sending messages to the API."""
    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("\nValidation mode - skipping API call")
        return

    from anthropic import Anthropic

    client = Anthropic()

    print("\nSending to Claude...")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=messages,
    )

    print("\nResponse structure:")
    print(f"  ID: {response.id}")
    print(f"  Model: {response.model}")
    print(f"  Stop reason: {response.stop_reason}")
    print(f"  Content blocks: {len(response.content)}")

    print("\nResponse text:")
    print(f"  {response.content[0].text[:200]}...")


def main():
    messages = demonstrate_message_structure()
    demonstrate_api_call(messages)


if __name__ == "__main__":
    main()
