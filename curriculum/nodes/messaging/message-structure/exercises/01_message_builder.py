"""
Exercise 1: Message Builder

Goal: Build and validate message structures programmatically.

Instructions:
1. Create a ConversationBuilder class
2. Add methods for user and assistant messages
3. Validate message ordering rules

Challenge:
- Add content block support
- Implement message serialization/deserialization
"""


class ConversationBuilder:
    """
    TODO: Implement a conversation builder.

    Requirements:
    - add_user(content) - add a user message
    - add_assistant(content) - add an assistant message
    - validate() - check message ordering rules
    - build() - return the messages array
    """

    def __init__(self):
        self.messages = []

    def add_user(self, content: str) -> "ConversationBuilder":
        """Add a user message."""
        self.messages.append({"role": "user", "content": content})
        return self

    def add_assistant(self, content: str) -> "ConversationBuilder":
        """Add an assistant message."""
        self.messages.append({"role": "assistant", "content": content})
        return self

    def validate(self) -> tuple[bool, str]:
        """
        Validate message structure.

        Rules:
        1. First message must be from user
        2. Messages must alternate roles
        3. Cannot have empty messages array
        """
        if not self.messages:
            return False, "No messages"

        if self.messages[0]["role"] != "user":
            return False, "First message must be from user"

        for i in range(1, len(self.messages)):
            if self.messages[i]["role"] == self.messages[i - 1]["role"]:
                return False, f"Messages must alternate roles (position {i})"

        return True, "Valid"

    def build(self) -> list[dict]:
        """Return the messages array."""
        return self.messages.copy()

    def clear(self) -> "ConversationBuilder":
        """Clear all messages."""
        self.messages = []
        return self


def test_conversation_builder():
    """Test the ConversationBuilder class."""
    print("Testing ConversationBuilder...")
    print()

    # Test 1: Valid conversation
    print("Test 1: Valid conversation")
    builder = ConversationBuilder()
    builder.add_user("Hello").add_assistant("Hi there!").add_user("How are you?")

    valid, msg = builder.validate()
    print(f"  Messages: {len(builder.build())}")
    print(f"  Valid: {valid} - {msg}")
    assert valid, "Should be valid"
    print("  ✓ Passed")
    print()

    # Test 2: Invalid - starts with assistant
    print("Test 2: Invalid - starts with assistant")
    builder.clear()
    builder.add_assistant("Hello!")

    valid, msg = builder.validate()
    print(f"  Valid: {valid} - {msg}")
    assert not valid, "Should be invalid"
    print("  ✓ Passed")
    print()

    # Test 3: Invalid - consecutive user messages
    print("Test 3: Invalid - consecutive roles")
    builder.clear()
    builder.add_user("Hello").add_user("Hello again")

    valid, msg = builder.validate()
    print(f"  Valid: {valid} - {msg}")
    assert not valid, "Should be invalid"
    print("  ✓ Passed")
    print()

    print("All tests passed!")


def main():
    print("=" * 50)
    print("Exercise 1: Message Builder")
    print("=" * 50)
    print()
    test_conversation_builder()


if __name__ == "__main__":
    main()
