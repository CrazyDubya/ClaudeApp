# System Prompts

**Category:** Messaging
**Difficulty:** 2/5
**Estimated Time:** 45 minutes
**Prerequisites:** [Message Structure](../message-structure/)

---

## Learning Objectives

By the end of this node, you will:
- Design effective system prompts for different use cases
- Understand system prompt best practices
- Structure prompts for consistency and reliability

---

## Concept Overview

A **system prompt** sets the context, personality, and constraints for Claude's responses. It's provided separately from the conversation messages and influences all of Claude's responses in the session.

### System Prompt vs. User Messages

| Aspect | System Prompt | User Messages |
|--------|---------------|---------------|
| Purpose | Set behavior and context | Provide specific requests |
| Persistence | Applies to entire conversation | Per-message |
| Visibility | Not shown to end users typically | Part of conversation |
| Token usage | Counted once per request | Counted per message |

---

## Key Patterns

### Basic System Prompt

```python
from anthropic import Anthropic

client = Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="You are a helpful coding assistant. Provide clear, concise code examples.",
    messages=[
        {"role": "user", "content": "How do I read a file in Python?"}
    ]
)
```

### Structured System Prompt

```python
system_prompt = """You are a customer support assistant for TechCorp.

## Your Role
- Answer questions about TechCorp products
- Help troubleshoot common issues
- Escalate complex issues to human support

## Guidelines
- Be friendly and professional
- Keep responses concise (under 200 words)
- Always verify the customer's product model before troubleshooting

## Constraints
- Never share internal pricing or discount information
- Do not make promises about future product features
- If unsure, recommend contacting support@techcorp.com
"""

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=system_prompt,
    messages=[{"role": "user", "content": "My device won't turn on"}]
)
```

---

## System Prompt Components

### 1. Role Definition

Define who or what Claude should act as:

```
You are a senior Python developer with 10 years of experience.
You specialize in web development and data science.
```

### 2. Task Description

Explain what Claude should do:

```
Your job is to review code submissions and provide:
- A summary of what the code does
- Potential bugs or issues
- Suggestions for improvement
```

### 3. Constraints and Guidelines

Set boundaries and rules:

```
Guidelines:
- Use Python 3.10+ syntax
- Follow PEP 8 style guidelines
- Prefer standard library over external packages when possible

Constraints:
- Do not execute or run any code
- Do not access external URLs or APIs
- Keep examples under 50 lines
```

### 4. Output Format

Specify how responses should be structured:

```
Format your response as:
1. **Summary**: One sentence overview
2. **Details**: Detailed explanation
3. **Example**: Code example if applicable
```

---

## Best Practices

### Be Specific

```python
# Too vague
system = "Be helpful"

# Better
system = """You are a technical writing assistant.
Help users improve their documentation by:
- Clarifying unclear sentences
- Suggesting better structure
- Fixing grammar and spelling
Maintain the original technical accuracy."""
```

### Use Positive Instructions

```python
# Negative (less effective)
system = "Don't be verbose. Don't use jargon. Don't ramble."

# Positive (more effective)
system = """Keep responses concise and focused.
Use plain language accessible to beginners.
Get to the point quickly."""
```

### Provide Examples

```python
system = """You are a SQL query assistant.

When users describe what data they want, provide the SQL query.

Example:
User: "Get all users who signed up this month"
Assistant:
```sql
SELECT * FROM users
WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE);
```
"""
```

---

## Common Pitfalls

1. **Overly long prompts**: Keep system prompts focused; don't include everything
2. **Contradictory instructions**: Ensure all guidelines are consistent
3. **Missing context**: Provide enough background for Claude to understand the domain
4. **No output format**: Without format guidance, responses may be inconsistent

---

## Exercises

1. **Customer Support Bot** (`exercises/01_support_bot.py`): Design a system prompt for a support chatbot
2. **Code Reviewer** (`exercises/02_code_reviewer.py`): Create a system prompt for code review
3. **Prompt Refinement** (`exercises/03_prompt_refinement.py`): Iterate and improve a system prompt

---

## Next Steps

After completing this node, proceed to:
- [Multi-turn Conversations](../multi-turn/) - Maintain context across turns
- [Streaming Responses](../streaming/) - Real-time response handling
