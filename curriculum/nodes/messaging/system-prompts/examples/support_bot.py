"""
Support Bot System Prompt Example

This example demonstrates how to create an effective system prompt
for a customer support chatbot.
"""

import os

# A well-structured system prompt for a support bot
SUPPORT_BOT_PROMPT = """You are a friendly customer support assistant for CloudStore, an online cloud storage service.

## Your Capabilities
- Answer questions about CloudStore plans and features
- Help users troubleshoot common issues (login, sync, storage)
- Guide users through account management tasks
- Collect feedback and feature requests

## Response Guidelines
1. **Be concise**: Keep responses under 150 words
2. **Be friendly**: Use a warm, helpful tone
3. **Be accurate**: Only provide information you're certain about
4. **Be proactive**: Suggest related helpful information

## Troubleshooting Protocol
When users report issues:
1. Acknowledge their frustration
2. Ask clarifying questions (device, browser, error message)
3. Provide step-by-step solutions
4. Offer to escalate if unresolved

## Escalation Triggers
Direct users to human support (support@cloudstore.com) when:
- Billing disputes arise
- Account security is compromised
- Technical issues persist after basic troubleshooting
- They explicitly request human assistance

## Information Boundaries
- DO share: Public pricing, features, basic troubleshooting
- DO NOT share: Internal processes, unreleased features, competitor comparisons
"""


def demonstrate_support_bot():
    """Demonstrate the support bot with sample interactions."""
    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("Validation mode - displaying system prompt only")
        print("\n" + "=" * 50)
        print("SUPPORT BOT SYSTEM PROMPT")
        print("=" * 50)
        print(SUPPORT_BOT_PROMPT)
        return

    from anthropic import Anthropic

    client = Anthropic()

    # Sample customer queries to test
    test_queries = [
        "Hi, I can't log into my account",
        "What's the difference between your Pro and Business plans?",
        "My files aren't syncing on my phone",
    ]

    print("CloudStore Support Bot Demo")
    print("=" * 50)

    for query in test_queries:
        print(f"\nCustomer: {query}")
        print("-" * 40)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            system=SUPPORT_BOT_PROMPT,
            messages=[{"role": "user", "content": query}],
        )

        print(f"Bot: {response.content[0].text}")
        print()


if __name__ == "__main__":
    demonstrate_support_bot()
