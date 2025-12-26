"""
Token Counter Example

This example demonstrates how to count and monitor token usage
for effective context window management.
"""

import os


def estimate_tokens(text: str) -> int:
    """
    Estimate token count without API call.

    This is a rough estimate based on ~4 characters per token
    for English text. Actual counts may vary.
    """
    return len(text) // 4


def count_message_tokens(messages: list) -> dict:
    """
    Count tokens in a message array.

    Returns breakdown by role and total.
    """
    user_tokens = 0
    assistant_tokens = 0

    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, list):
            # Handle content blocks
            content = " ".join(
                block.get("text", "") for block in content if block.get("type") == "text"
            )
        tokens = estimate_tokens(content)

        if msg["role"] == "user":
            user_tokens += tokens
        else:
            assistant_tokens += tokens

    return {
        "user_tokens": user_tokens,
        "assistant_tokens": assistant_tokens,
        "total_tokens": user_tokens + assistant_tokens,
    }


def check_context_budget(
    messages: list,
    system_prompt: str = "",
    max_context: int = 200000,
    reserve_output: int = 4096
) -> dict:
    """
    Check if messages fit within context budget.

    Args:
        messages: Conversation messages
        system_prompt: System prompt text
        max_context: Maximum context window size
        reserve_output: Tokens to reserve for response

    Returns:
        Budget analysis dictionary
    """
    message_counts = count_message_tokens(messages)
    system_tokens = estimate_tokens(system_prompt)

    total_input = message_counts["total_tokens"] + system_tokens
    available = max_context - reserve_output
    remaining = available - total_input

    return {
        "system_tokens": system_tokens,
        "message_tokens": message_counts["total_tokens"],
        "total_input": total_input,
        "available_context": available,
        "remaining_budget": remaining,
        "usage_percent": (total_input / available) * 100,
        "within_budget": remaining > 0,
    }


def display_budget_report(budget: dict):
    """Display a formatted budget report."""
    print("\nContext Budget Report")
    print("=" * 40)
    print(f"System prompt:     {budget['system_tokens']:>8} tokens")
    print(f"Messages:          {budget['message_tokens']:>8} tokens")
    print(f"Total input:       {budget['total_input']:>8} tokens")
    print("-" * 40)
    print(f"Available context: {budget['available_context']:>8} tokens")
    print(f"Remaining budget:  {budget['remaining_budget']:>8} tokens")
    print(f"Usage:             {budget['usage_percent']:>7.1f}%")
    print("-" * 40)
    status = "Within budget" if budget["within_budget"] else "OVER BUDGET"
    print(f"Status: {status}")


def main():
    print("Token Counter Example")
    print("=" * 40)

    # Example conversation
    system_prompt = """You are a helpful assistant for software development.
    Provide clear, concise explanations with code examples when appropriate."""

    messages = [
        {"role": "user", "content": "What is a Python decorator?"},
        {
            "role": "assistant",
            "content": "A Python decorator is a function that takes another function as input and extends its behavior without explicitly modifying it. Decorators use the @decorator_name syntax above a function definition.",
        },
        {"role": "user", "content": "Can you show me an example?"},
        {
            "role": "assistant",
            "content": """Here's a simple timing decorator:

```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
```""",
        },
        {"role": "user", "content": "How do decorators work with arguments?"},
    ]

    # Count tokens
    print("\nMessage token breakdown:")
    for i, msg in enumerate(messages):
        tokens = estimate_tokens(msg["content"])
        role = msg["role"]
        preview = msg["content"][:40].replace("\n", " ") + "..."
        print(f"  {i + 1}. [{role:9}] {tokens:4} tokens | {preview}")

    # Check budget
    budget = check_context_budget(messages, system_prompt)
    display_budget_report(budget)

    # Show what happens with a very long conversation
    print("\n" + "=" * 40)
    print("Simulating conversation growth...")

    # Simulate adding more messages
    for i in range(20):
        messages.append({"role": "user", "content": "Tell me more about this topic. " * 20})
        messages.append(
            {
                "role": "assistant",
                "content": "Here's more information about the topic. " * 30,
            }
        )

    budget = check_context_budget(messages, system_prompt)
    display_budget_report(budget)


if __name__ == "__main__":
    main()
