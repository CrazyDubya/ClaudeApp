"""
Exercise 1: Model Comparison

Goal: Compare responses from different Claude models.

Instructions:
1. Send the same prompt to Haiku and Sonnet
2. Compare response quality, length, and latency
3. Understand when to use each model

Challenge:
- Create a comparison table
- Test with different types of prompts
"""

import os
import time


def compare_models(prompt: str):
    """
    TODO: Compare responses from different models.

    Send the same prompt to:
    - claude-3-5-haiku-20241022 (fast, economical)
    - claude-sonnet-4-20250514 (balanced)

    Compare:
    - Response quality
    - Response time
    - Token usage
    """
    from anthropic import Anthropic

    client = Anthropic()

    models = [
        ("Haiku", "claude-3-5-haiku-20241022"),
        ("Sonnet", "claude-sonnet-4-20250514"),
    ]

    results = []

    for name, model_id in models:
        print(f"\nTesting {name}...")
        start = time.time()

        message = client.messages.create(
            model=model_id,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )

        elapsed = time.time() - start

        results.append(
            {
                "name": name,
                "model": model_id,
                "response": message.content[0].text,
                "latency_ms": elapsed * 1000,
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }
        )

    return results


def display_comparison(results: list):
    """Display comparison results."""
    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)

    for r in results:
        print(f"\n{r['name']} ({r['model']})")
        print("-" * 40)
        print(f"Latency:     {r['latency_ms']:.0f} ms")
        print(f"Tokens:      {r['input_tokens']} in / {r['output_tokens']} out")
        print(f"Response:")
        # Show first 200 chars
        text = r["response"]
        print(f"  {text[:200]}{'...' if len(text) > 200 else ''}")


def test_different_tasks():
    """
    TODO: Test models with different task types.

    Try:
    - Simple question (Haiku should be fine)
    - Complex reasoning (Sonnet may be better)
    - Creative writing (compare quality)
    """
    tasks = [
        ("Simple", "What is 2 + 2?"),
        ("Moderate", "Explain how a hash table works in 2-3 sentences."),
        ("Complex", "Compare and contrast REST and GraphQL APIs, with pros and cons of each."),
    ]

    print("\n" + "=" * 60)
    print("TASK COMPLEXITY COMPARISON")
    print("=" * 60)

    for task_name, prompt in tasks:
        print(f"\n### {task_name} Task ###")
        print(f"Prompt: {prompt[:50]}...")
        results = compare_models(prompt)
        display_comparison(results)


def main():
    print("=" * 50)
    print("Exercise 1: Model Comparison")
    print("=" * 50)

    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("\nValidation mode - skipping API calls")
        return

    # Basic comparison
    prompt = "Explain what a Python decorator is in 2-3 sentences."
    print(f"\nPrompt: {prompt}")

    results = compare_models(prompt)
    display_comparison(results)

    # Uncomment to test different task types:
    # test_different_tasks()


if __name__ == "__main__":
    main()
