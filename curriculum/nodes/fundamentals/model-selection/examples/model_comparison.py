"""
Model Comparison Example

This example demonstrates how to compare responses from different
Claude models to understand their characteristics.
"""

import os
import time
from typing import NamedTuple


class ModelResult(NamedTuple):
    """Result from a model request."""

    model: str
    response: str
    latency_ms: float
    input_tokens: int
    output_tokens: int


def compare_models(prompt: str) -> list[ModelResult]:
    """
    Send the same prompt to different models and compare results.

    Args:
        prompt: The prompt to send to each model.

    Returns:
        List of results from each model.
    """
    from anthropic import Anthropic

    client = Anthropic()

    models = [
        "claude-3-5-haiku-20241022",
        "claude-sonnet-4-20250514",
        # "claude-opus-4-20250514",  # Uncomment to include Opus
    ]

    results = []

    for model in models:
        print(f"Testing {model}...")

        start_time = time.time()

        message = client.messages.create(
            model=model,
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )

        latency_ms = (time.time() - start_time) * 1000

        result = ModelResult(
            model=model,
            response=message.content[0].text,
            latency_ms=latency_ms,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
        )
        results.append(result)

    return results


def display_results(results: list[ModelResult]) -> None:
    """Display comparison results in a formatted table."""
    print("\n" + "=" * 60)
    print("MODEL COMPARISON RESULTS")
    print("=" * 60)

    for result in results:
        print(f"\n{result.model}")
        print("-" * 40)
        print(f"Latency: {result.latency_ms:.0f}ms")
        print(f"Tokens: {result.input_tokens} in / {result.output_tokens} out")
        print(f"Response:\n{result.response[:200]}...")


def main():
    # Skip in validation mode
    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("Validation mode - skipping API calls")
        print("This example compares responses from different Claude models")
        return

    prompt = "Explain what an API is in 2-3 sentences."

    print("Model Comparison Example")
    print("=" * 40)
    print(f"Prompt: {prompt}\n")

    results = compare_models(prompt)
    display_results(results)


if __name__ == "__main__":
    main()
