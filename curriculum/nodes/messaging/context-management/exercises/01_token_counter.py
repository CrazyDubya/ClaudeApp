"""
Exercise 1: Token Counter

Goal: Build a utility to count and manage token usage.

Instructions:
1. Implement token estimation
2. Track usage across multiple requests
3. Warn when approaching limits

Challenge:
- Implement conversation trimming when over budget
- Add cost estimation
"""


class TokenCounter:
    """
    TODO: Implement a token counter and budget tracker.

    Requirements:
    - Estimate tokens in text
    - Track cumulative usage
    - Warn at threshold
    """

    # Approximate costs per 1M tokens (as of 2024)
    COSTS = {
        "claude-3-5-haiku-20241022": {"input": 0.25, "output": 1.25},
        "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
        "claude-opus-4-20250514": {"input": 15.0, "output": 75.0},
    }

    def __init__(self, budget_tokens: int = 100000):
        self.budget = budget_tokens
        self.input_tokens = 0
        self.output_tokens = 0
        self.requests = 0

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count for text.
        Rough estimate: ~4 characters per token for English.
        """
        return len(text) // 4

    def record(self, input_tokens: int, output_tokens: int):
        """Record token usage from a request."""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.requests += 1

        # Check budget
        total = self.input_tokens + self.output_tokens
        if total > self.budget * 0.9:
            print(f"⚠ Token budget warning: {total}/{self.budget} used")

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def remaining(self) -> int:
        return self.budget - self.total_tokens

    def estimate_cost(self, model: str = "claude-sonnet-4-20250514") -> float:
        """Estimate cost in USD."""
        if model not in self.COSTS:
            return 0.0

        costs = self.COSTS[model]
        input_cost = (self.input_tokens / 1_000_000) * costs["input"]
        output_cost = (self.output_tokens / 1_000_000) * costs["output"]
        return input_cost + output_cost

    def summary(self) -> dict:
        """Get usage summary."""
        return {
            "requests": self.requests,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "budget": self.budget,
            "remaining": self.remaining,
            "usage_percent": (self.total_tokens / self.budget) * 100,
        }

    def print_summary(self, model: str = "claude-sonnet-4-20250514"):
        """Print formatted summary."""
        s = self.summary()
        cost = self.estimate_cost(model)

        print("\n📊 Token Usage Summary")
        print("=" * 40)
        print(f"Requests:      {s['requests']}")
        print(f"Input tokens:  {s['input_tokens']:,}")
        print(f"Output tokens: {s['output_tokens']:,}")
        print(f"Total tokens:  {s['total_tokens']:,}")
        print(f"Budget:        {s['budget']:,}")
        print(f"Remaining:     {s['remaining']:,}")
        print(f"Usage:         {s['usage_percent']:.1f}%")
        print(f"Est. cost:     ${cost:.4f}")


def trim_messages(messages: list, max_tokens: int) -> list:
    """
    TODO: Trim messages to fit within token budget.

    Strategy:
    - Always keep the first message (important context)
    - Remove oldest messages until under budget
    """
    if not messages:
        return messages

    # Calculate current tokens
    total = sum(TokenCounter.estimate_tokens(m["content"]) for m in messages)

    if total <= max_tokens:
        return messages

    # Keep first message, trim from the middle
    result = [messages[0]]
    remaining_budget = max_tokens - TokenCounter.estimate_tokens(messages[0]["content"])

    # Add messages from the end until budget exhausted
    for msg in reversed(messages[1:]):
        msg_tokens = TokenCounter.estimate_tokens(msg["content"])
        if msg_tokens <= remaining_budget:
            result.insert(1, msg)
            remaining_budget -= msg_tokens

    return result


def test_token_counter():
    """Test the TokenCounter class."""
    print("Testing TokenCounter...")

    counter = TokenCounter(budget_tokens=10000)

    # Simulate some requests
    counter.record(input_tokens=150, output_tokens=300)
    counter.record(input_tokens=200, output_tokens=450)
    counter.record(input_tokens=100, output_tokens=200)

    counter.print_summary()

    # Test estimation
    text = "This is a sample text for token estimation."
    estimated = TokenCounter.estimate_tokens(text)
    print(f"\nEstimated tokens for '{text}': {estimated}")


def test_message_trimming():
    """Test message trimming."""
    print("\nTesting message trimming...")

    messages = [
        {"role": "user", "content": "This is the first important message."},
        {"role": "assistant", "content": "Response 1 " * 50},
        {"role": "user", "content": "Second message " * 30},
        {"role": "assistant", "content": "Response 2 " * 50},
        {"role": "user", "content": "Third message " * 20},
        {"role": "assistant", "content": "Response 3 " * 40},
        {"role": "user", "content": "Latest message"},
    ]

    original_tokens = sum(TokenCounter.estimate_tokens(m["content"]) for m in messages)
    print(f"Original: {len(messages)} messages, ~{original_tokens} tokens")

    trimmed = trim_messages(messages, max_tokens=500)
    trimmed_tokens = sum(TokenCounter.estimate_tokens(m["content"]) for m in trimmed)
    print(f"Trimmed:  {len(trimmed)} messages, ~{trimmed_tokens} tokens")


def main():
    print("=" * 50)
    print("Exercise 1: Token Counter")
    print("=" * 50)

    test_token_counter()
    test_message_trimming()


if __name__ == "__main__":
    main()
