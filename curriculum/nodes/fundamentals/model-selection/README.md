# Model Selection

**Category:** Fundamentals
**Difficulty:** 2/5
**Estimated Time:** 30 minutes
**Prerequisites:** [Your First Message](../first-message/)

---

## Learning Objectives

By the end of this node, you will:
- Understand the differences between Claude model tiers
- Choose the right model for your use case
- Balance capability, speed, and cost

---

## Concept Overview

Anthropic offers multiple Claude models optimized for different use cases. Selecting the right model is a key architectural decision that affects your application's performance, cost, and capabilities.

### Model Tiers

| Model | Best For | Relative Speed | Relative Cost |
|-------|----------|----------------|---------------|
| **Claude Opus 4** | Complex reasoning, research, coding | Slower | Higher |
| **Claude Sonnet 4** | Balanced performance, most use cases | Medium | Medium |
| **Claude Haiku 3.5** | Fast responses, high volume, simple tasks | Fastest | Lowest |

---

## Key Patterns

### Specifying a Model

```python
from anthropic import Anthropic

client = Anthropic()

# Use Sonnet for balanced performance
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)

# Use Haiku for quick, simple tasks
message = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=256,
    messages=[{"role": "user", "content": "Summarize this in one sentence: ..."}]
)

# Use Opus for complex reasoning
message = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Analyze this codebase and suggest architectural improvements: ..."}]
)
```

### Dynamic Model Selection

```python
def select_model(task_complexity: str) -> str:
    """Select appropriate model based on task complexity."""
    models = {
        "simple": "claude-3-5-haiku-20241022",
        "moderate": "claude-sonnet-4-20250514",
        "complex": "claude-opus-4-20250514",
    }
    return models.get(task_complexity, "claude-sonnet-4-20250514")


# Use based on task
model = select_model("moderate")
message = client.messages.create(
    model=model,
    max_tokens=1024,
    messages=[{"role": "user", "content": "..."}]
)
```

---

## Decision Framework

### Choose Haiku When:
- Response speed is critical
- Tasks are straightforward (classification, extraction, simple Q&A)
- Processing high volumes of requests
- Cost optimization is a priority

### Choose Sonnet When:
- You need balanced performance
- Tasks involve moderate reasoning
- Building general-purpose applications
- Default choice for most applications

### Choose Opus When:
- Complex multi-step reasoning is required
- High-quality code generation or review
- Research and analysis tasks
- Accuracy is more important than speed

---

## Context Window Considerations

All current Claude models support large context windows:

| Model | Context Window |
|-------|----------------|
| Claude Opus 4 | 200K tokens |
| Claude Sonnet 4 | 200K tokens |
| Claude Haiku 3.5 | 200K tokens |

For applications processing large documents, all models can handle substantial input. The choice depends more on task complexity than context size.

---

## Cost Optimization Strategies

### 1. Model Routing

Route requests to different models based on task complexity:

```python
def route_request(query: str, context_length: int) -> str:
    """Route to appropriate model based on request characteristics."""
    # Simple queries with short context -> Haiku
    if len(query) < 100 and context_length < 1000:
        return "claude-3-5-haiku-20241022"

    # Complex queries or large context -> Opus
    if "analyze" in query.lower() or "explain in detail" in query.lower():
        return "claude-opus-4-20250514"

    # Default to Sonnet
    return "claude-sonnet-4-20250514"
```

### 2. Cascading

Start with a faster model and escalate if needed:

```python
def cascading_request(messages: list) -> str:
    """Try faster model first, escalate if response quality is low."""
    # Try Haiku first
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=1024,
        messages=messages
    )

    # Check if response needs more sophisticated handling
    if needs_escalation(response):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=messages
        )

    return response.content[0].text
```

---

## Common Pitfalls

1. **Over-using Opus**: Not every task needs the most powerful model
2. **Under-using Haiku**: Don't overlook Haiku for simple, high-volume tasks
3. **Hardcoding models**: Make model selection configurable for easy tuning
4. **Ignoring latency**: Consider user experience, not just output quality

---

## Exercises

1. **Model Comparison** (`exercises/01_model_comparison.py`): Compare responses from different models
2. **Cost Calculator** (`exercises/02_cost_calculator.py`): Estimate costs for your use case
3. **Model Router** (`exercises/03_model_router.py`): Implement a simple model routing strategy

---

## Next Steps

After completing this node, proceed to:
- [Message Structure](../../messaging/message-structure/) - Deep dive into message formatting
- [Streaming Responses](../../messaging/streaming/) - Real-time response handling
