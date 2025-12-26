"""
Exercise 1: Hello Claude

Goal: Send your first message to Claude and receive a response.

Instructions:
1. Create an Anthropic client
2. Send a simple greeting message
3. Print the response

Challenge:
- Experiment with different greetings
- Try changing max_tokens and observe the effect
"""

import os


def send_first_message():
    """
    TODO: Implement your first message to Claude.

    Requirements:
    - Create an Anthropic client
    - Send a message asking Claude to introduce itself
    - Return the response text
    """
    from anthropic import Anthropic

    client = Anthropic()

    # YOUR CODE HERE - modify the message content
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[
            {"role": "user", "content": "Hello! Please introduce yourself briefly."}
        ],
    )

    return message.content[0].text


def explore_max_tokens():
    """
    TODO: Explore how max_tokens affects responses.

    Try different values: 50, 100, 500
    Observe how the response changes.
    """
    from anthropic import Anthropic

    client = Anthropic()

    prompt = "Explain what an API is."

    for max_tokens in [50, 100, 500]:
        print(f"\n--- max_tokens={max_tokens} ---")

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        response = message.content[0].text
        print(f"Response ({len(response)} chars):")
        print(response[:200] + "..." if len(response) > 200 else response)
        print(f"Stop reason: {message.stop_reason}")


def main():
    print("=" * 50)
    print("Exercise 1: Hello Claude")
    print("=" * 50)

    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("\nValidation mode - skipping API calls")
        print("This exercise sends your first message to Claude")
        return

    print("\n1. Sending first message...")
    response = send_first_message()
    print(f"\nClaude says:\n{response}")

    print("\n" + "=" * 50)
    print("2. Exploring max_tokens...")
    explore_max_tokens()


if __name__ == "__main__":
    main()
