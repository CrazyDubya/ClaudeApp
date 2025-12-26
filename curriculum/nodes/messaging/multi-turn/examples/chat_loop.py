"""
Chat Loop Example

This example demonstrates a simple multi-turn conversation loop
that maintains context across messages.
"""

import os


class ChatSession:
    """A simple multi-turn chat session."""

    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt
        self.messages = []
        self.client = None

    def _get_client(self):
        """Lazy initialization of the Anthropic client."""
        if self.client is None:
            from anthropic import Anthropic

            self.client = Anthropic()
        return self.client

    def send(self, user_input: str) -> str:
        """Send a message and get a response."""
        # Add user message to history
        self.messages.append({"role": "user", "content": user_input})

        # Create the API request
        client = self._get_client()
        kwargs = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1024,
            "messages": self.messages,
        }
        if self.system_prompt:
            kwargs["system"] = self.system_prompt

        response = client.messages.create(**kwargs)

        # Extract and store the response
        assistant_message = response.content[0].text
        self.messages.append({"role": "assistant", "content": assistant_message})

        return assistant_message

    def get_turn_count(self) -> int:
        """Get the number of conversation turns."""
        return len(self.messages) // 2

    def reset(self):
        """Clear the conversation history."""
        self.messages = []


def run_interactive_chat():
    """Run an interactive chat loop."""
    print("Multi-turn Chat Demo")
    print("=" * 40)
    print("Type 'quit' to exit, 'reset' to start over\n")

    session = ChatSession(
        system_prompt="You are a helpful assistant. Keep responses brief and friendly."
    )

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        if user_input.lower() == "reset":
            session.reset()
            print("Conversation reset.\n")
            continue

        response = session.send(user_input)
        print(f"Claude: {response}\n")
        print(f"  (Turn {session.get_turn_count()})")
        print()


def run_demo():
    """Run a scripted demo of multi-turn conversation."""
    print("Multi-turn Conversation Demo")
    print("=" * 40)

    session = ChatSession(
        system_prompt="You are a helpful Python tutor. Give concise explanations."
    )

    demo_messages = [
        "What is a Python list?",
        "How do I add an item to it?",
        "What about removing items?",
    ]

    for msg in demo_messages:
        print(f"\nYou: {msg}")
        response = session.send(msg)
        print(f"Claude: {response}")
        print(f"  (Turn {session.get_turn_count()}, History: {len(session.messages)} messages)")


def main():
    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("Validation mode - displaying chat structure")
        print("\nThis example demonstrates multi-turn conversations where")
        print("conversation history is maintained across messages.")
        return

    # Check if running interactively
    import sys

    if sys.stdin.isatty():
        run_interactive_chat()
    else:
        run_demo()


if __name__ == "__main__":
    main()
