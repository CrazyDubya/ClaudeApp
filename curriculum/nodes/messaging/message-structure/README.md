# Message Structure

**Category:** Messaging
**Difficulty:** 2/5
**Estimated Time:** 25 minutes
**Prerequisites:** [Your First Message](../../fundamentals/first-message/)

---

## Learning Objectives

By the end of this node, you will:
- Understand message roles and their purposes
- Work with different content types
- Structure conversations correctly

---

## Concept Overview

Messages in the Claude API follow a structured format. Each message has a **role** and **content**, and conversations are built as arrays of these messages.

### Message Roles

| Role | Purpose | Who Creates It |
|------|---------|----------------|
| `user` | Input from the human user | Your application |
| `assistant` | Responses from Claude | The API (or your app for context) |

Note: System prompts use a separate `system` parameter, not the messages array.

---

## Key Patterns

### Basic Message Structure

```python
messages = [
    {"role": "user", "content": "Hello, Claude!"},
]

# After getting a response, continue the conversation:
messages = [
    {"role": "user", "content": "Hello, Claude!"},
    {"role": "assistant", "content": "Hello! How can I help you today?"},
    {"role": "user", "content": "Tell me about Python."},
]
```

### Text Content

The simplest content type is a string:

```python
message = {"role": "user", "content": "What is machine learning?"}
```

### Structured Content Blocks

For richer content, use content blocks:

```python
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "What do you see in this image?"},
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": "<base64-encoded-image>",
            },
        },
    ],
}
```

### Content Block Types

| Type | Purpose | Covered In |
|------|---------|------------|
| `text` | Plain text content | This node |
| `image` | Image data | [Vision](../vision/) |
| `tool_use` | Tool call from Claude | [Tools](../../tools/) |
| `tool_result` | Your tool's response | [Tools](../../tools/) |

---

## Response Structure

Claude's responses have a consistent structure:

```python
response = client.messages.create(...)

# Key response fields
response.id              # Unique message ID (e.g., "msg_abc123")
response.type            # Always "message"
response.role            # Always "assistant"
response.content         # List of content blocks
response.model           # Model used (e.g., "claude-sonnet-4-20250514")
response.stop_reason     # Why generation stopped
response.usage           # Token counts
```

### Stop Reasons

| Reason | Meaning |
|--------|---------|
| `end_turn` | Claude finished its response naturally |
| `max_tokens` | Hit the max_tokens limit |
| `stop_sequence` | Hit a custom stop sequence |
| `tool_use` | Claude wants to use a tool |

### Accessing Content

```python
# Single text response (most common)
text = response.content[0].text

# Handle multiple content blocks
for block in response.content:
    if block.type == "text":
        print(block.text)
    elif block.type == "tool_use":
        print(f"Tool: {block.name}, Input: {block.input}")
```

---

## Message Ordering Rules

1. **Messages must alternate** between `user` and `assistant` roles
2. **First message must be from `user`**
3. **Last message should be from `user`** (what you want Claude to respond to)

```python
# Valid conversation
messages = [
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello!"},
    {"role": "user", "content": "How are you?"},  # Claude responds to this
]

# Invalid - two user messages in a row
messages = [
    {"role": "user", "content": "Hi"},
    {"role": "user", "content": "Hello?"},  # Error!
]
```

---

## Common Pitfalls

1. **Forgetting content is a list**: Response content is always a list, even for single text responses
2. **Wrong message order**: User and assistant messages must alternate
3. **Confusing system with messages**: System prompts use the `system` parameter, not messages
4. **Not handling all content types**: Claude may return tool_use blocks when tools are enabled

---

## Exercises

1. **Message Builder** (`exercises/01_message_builder.py`): Build a conversation programmatically
2. **Response Parser** (`exercises/02_response_parser.py`): Extract information from responses
3. **Content Types** (`exercises/03_content_types.py`): Work with different content block types

---

## Next Steps

After completing this node, proceed to:
- [System Prompts](../system-prompts/) - Design effective system prompts
- [Multi-turn Conversations](../multi-turn/) - Maintain context across turns
- [Streaming Responses](../streaming/) - Handle real-time streaming
