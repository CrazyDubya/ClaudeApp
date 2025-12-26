"""
Exercise 1: Customer Support Bot

Goal: Design an effective system prompt for a support chatbot.

Instructions:
1. Create a system prompt with role, guidelines, and constraints
2. Test with sample customer queries
3. Refine based on response quality

Challenge:
- Add escalation triggers
- Handle edge cases gracefully
"""

import os

# Template for building system prompts
SYSTEM_PROMPT_TEMPLATE = """You are {role}.

## Your Responsibilities
{responsibilities}

## Response Guidelines
{guidelines}

## Constraints
{constraints}
"""


def create_support_prompt(
    company_name: str = "TechCorp",
    product: str = "cloud storage service",
) -> str:
    """
    TODO: Create a support bot system prompt.

    Fill in the template with appropriate:
    - Role description
    - Responsibilities
    - Guidelines
    - Constraints
    """
    return SYSTEM_PROMPT_TEMPLATE.format(
        role=f"a friendly customer support assistant for {company_name}, a {product}",
        responsibilities="""- Answer questions about our products and services
- Help troubleshoot common issues
- Guide users through account management
- Collect feedback and escalate complex issues""",
        guidelines="""- Be concise: Keep responses under 150 words
- Be empathetic: Acknowledge customer frustrations
- Be proactive: Suggest related helpful information
- Be clear: Use simple, jargon-free language""",
        constraints="""- Never share internal processes or unreleased features
- Never make promises about timelines or outcomes
- Always recommend contacting support@techcorp.com for billing issues
- If unsure, say so and offer to escalate""",
    )


def test_support_bot(system_prompt: str, queries: list[str]):
    """Test the support bot with sample queries."""
    from anthropic import Anthropic

    client = Anthropic()

    print("Testing Support Bot")
    print("=" * 50)

    for query in queries:
        print(f"\nCustomer: {query}")
        print("-" * 40)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            system=system_prompt,
            messages=[{"role": "user", "content": query}],
        )

        print(f"Bot: {response.content[0].text}")


def evaluate_prompt_quality(system_prompt: str) -> dict:
    """
    TODO: Evaluate system prompt quality.

    Check for:
    - Clear role definition
    - Specific guidelines
    - Appropriate constraints
    - Professional tone
    """
    checks = {
        "has_role": "You are" in system_prompt,
        "has_guidelines": "guideline" in system_prompt.lower(),
        "has_constraints": "constraint" in system_prompt.lower() or "never" in system_prompt.lower(),
        "reasonable_length": 200 < len(system_prompt) < 2000,
    }

    return checks


def main():
    print("=" * 50)
    print("Exercise 1: Customer Support Bot")
    print("=" * 50)

    # Create the prompt
    prompt = create_support_prompt()
    print("\nGenerated System Prompt:")
    print("-" * 40)
    print(prompt)

    # Evaluate
    print("\nPrompt Quality Check:")
    checks = evaluate_prompt_quality(prompt)
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")

    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("\nValidation mode - skipping API calls")
        return

    # Test with sample queries
    test_queries = [
        "How do I reset my password?",
        "Why is my bill so high this month?",
        "Your service is terrible! I want a refund!",
    ]

    test_support_bot(prompt, test_queries)


if __name__ == "__main__":
    main()
