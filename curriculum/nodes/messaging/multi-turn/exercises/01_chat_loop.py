"""
Exercise 1: Chat Loop

Goal: Build a multi-turn conversation loop that maintains context.

Instructions:
1. Create a conversation history list
2. Add user messages and store assistant responses
3. Send full history with each request

Challenge:
- Add conversation commands (/reset, /history, /quit)
- Implement conversation persistence to file
"""

import os
import json


class ChatBot:
    """
    TODO: Implement a multi-turn chatbot.

    Requirements:
    - Maintain conversation history
    - Send full history with each request
    - Support conversation reset
    """

    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt
        self.history = []
        self.client = None

    def _get_client(self):
        if self.client is None:
            from anthropic import Anthropic
            self.client = Anthropic()
        return self.client

    def chat(self, user_input: str) -> str:
        """Send a message and get a response."""
        # Add user message to history
        self.history.append({"role": "user", "content": user_input})

        # Build request
        client = self._get_client()
        kwargs = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 500,
            "messages": self.history,
        }
        if self.system_prompt:
            kwargs["system"] = self.system_prompt

        # Get response
        response = client.messages.create(**kwargs)
        assistant_message = response.content[0].text

        # Store response in history
        self.history.append({"role": "assistant", "content": assistant_message})

        return assistant_message

    def reset(self):
        """Clear conversation history."""
        self.history = []

    def get_history(self) -> list:
        """Get conversation history."""
        return self.history.copy()

    def save_history(self, filepath: str):
        """Save history to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.history, f, indent=2)

    def load_history(self, filepath: str):
        """Load history from a JSON file."""
        with open(filepath, "r") as f:
            self.history = json.load(f)


def run_chat_loop():
    """Run an interactive chat loop."""
    print("Multi-turn Chat")
    print("Commands: /reset, /history, /save, /quit")
    print("-" * 40)

    bot = ChatBot(system_prompt="You are a helpful assistant. Be concise.")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.startswith("/"):
            cmd = user_input.lower()
            if cmd == "/quit":
                print("Goodbye!")
                break
            elif cmd == "/reset":
                bot.reset()
                print("Conversation reset.")
                continue
            elif cmd == "/history":
                print(f"\nHistory ({len(bot.history)} messages):")
                for msg in bot.history:
                    role = msg["role"].upper()
                    content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                    print(f"  [{role}] {content}")
                continue
            elif cmd == "/save":
                bot.save_history("/tmp/chat_history.json")
                print("History saved to /tmp/chat_history.json")
                continue

        # Regular message
        response = bot.chat(user_input)
        print(f"\nClaude: {response}")


def test_chat_bot():
    """Test the ChatBot class."""
    print("Testing ChatBot...")

    bot = ChatBot()

    # Simulate conversation
    messages = [
        "My name is Alice.",
        "What's my name?",
        "What was the first thing I told you?",
    ]

    for msg in messages:
        print(f"\nYou: {msg}")
        response = bot.chat(msg)
        print(f"Claude: {response}")

    print(f"\nTotal messages in history: {len(bot.history)}")


def main():
    print("=" * 50)
    print("Exercise 1: Chat Loop")
    print("=" * 50)

    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("\nValidation mode - skipping API calls")
        return

    import sys
    if sys.stdin.isatty():
        run_chat_loop()
    else:
        test_chat_bot()


if __name__ == "__main__":
    main()
