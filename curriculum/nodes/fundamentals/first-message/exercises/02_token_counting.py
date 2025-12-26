"""
Exercise 2: Token Counting

Goal: Understand token usage in Claude API responses.

Instructions:
1. Send a message and examine the usage field
2. Compare input vs output tokens
3. Calculate approximate cost

Challenge:
- Track tokens across multiple requests
- Build a simple token budget tracker
"""

import os


def examine_token_usage():
    """
    TODO: Send a message and examine token usage.

    The response object contains a 'usage' field with:
    - input_tokens: tokens in your request
    - output_tokens: tokens in Claude's response
    """
    from anthropic import Anthropic

    client = Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": "Write a haiku about programming.",
            }
        ],
    )

    print("Response:")
    print(message.content[0].text)
    print()

    # Examine usage
    print("Token Usage:")
    print(f"  Input tokens:  {message.usage.input_tokens}")
    print(f"  Output tokens: {message.usage.output_tokens}")
    print(f"  Total tokens:  {message.usage.input_tokens + message.usage.output_tokens}")

    return message.usage


class TokenBudgetTracker:
    """
    TODO: Implement a token budget tracker.

    Requirements:
    - Track cumulative input and output tokens
    - Warn when approaching a budget limit
    - Provide usage summary
    """

    def __init__(self, budget: int = 10000):
        self.budget = budget
        self.total_input = 0
        self.total_output = 0
        self.request_count = 0

    def record_usage(self, input_tokens: int, output_tokens: int):
        """Record tokens from a request."""
        self.total_input += input_tokens
        self.total_output += output_tokens
        self.request_count += 1

        # Check budget
        total = self.total_input + self.total_output
        if total > self.budget * 0.9:
            print(f"⚠ Warning: {total}/{self.budget} tokens used (90%+)")

    def get_summary(self) -> dict:
        """Get usage summary."""
        total = self.total_input + self.total_output
        return {
            "requests": self.request_count,
            "input_tokens": self.total_input,
            "output_tokens": self.total_output,
            "total_tokens": total,
            "budget_remaining": self.budget - total,
            "budget_percent": (total / self.budget) * 100,
        }

    def print_summary(self):
        """Print formatted summary."""
        s = self.get_summary()
        print(f"\nToken Budget Summary:")
        print(f"  Requests:    {s['requests']}")
        print(f"  Input:       {s['input_tokens']} tokens")
        print(f"  Output:      {s['output_tokens']} tokens")
        print(f"  Total:       {s['total_tokens']} tokens")
        print(f"  Remaining:   {s['budget_remaining']} tokens")
        print(f"  Used:        {s['budget_percent']:.1f}%")


def main():
    print("=" * 50)
    print("Exercise 2: Token Counting")
    print("=" * 50)

    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("\nValidation mode - skipping API calls")
        return

    print("\n1. Examining token usage...")
    usage = examine_token_usage()

    print("\n2. Testing budget tracker...")
    tracker = TokenBudgetTracker(budget=1000)
    tracker.record_usage(usage.input_tokens, usage.output_tokens)
    tracker.print_summary()


if __name__ == "__main__":
    main()
