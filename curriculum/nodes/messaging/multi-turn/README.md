# Multi-turn Conversations

**Category:** Messaging
**Difficulty:** 3/5
**Estimated Time:** 40 minutes
**Prerequisites:** [Message Structure](../message-structure/)

---

## Learning Objectives

By the end of this node, you will:
- Maintain conversation context across multiple turns
- Implement stateful conversation handling
- Handle conversation history efficiently

---

## Concept Overview

Multi-turn conversations allow Claude to remember previous messages and maintain context throughout an interaction. This is essential for chatbots, assistants, and any application requiring back-and-forth dialogue.

### How Context Works

Claude doesn't have persistent memory between API calls. To maintain context, you must send the **entire conversation history** with each request:

```
Request 1: [user message 1]
Request 2: [user message 1, assistant response 1, user message 2]
Request 3: [user message 1, assistant response 1, user message 2, assistant response 2, user message 3]
```

---

## Key Patterns

### Basic Multi-turn Loop

```python
from anthropic import Anthropic

client = Anthropic()
conversation_history = []

def chat(user_message: str) -> str:
    """Send a message and get a response, maintaining history."""
    # Add user message to history
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # Send full history to Claude
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=conversation_history
    )

    # Extract and store assistant response
    assistant_message = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message

# Usage
print(chat("Hi, I'm learning Python"))
print(chat("What should I learn first?"))  # Claude remembers the context
print(chat("Can you give me an example?"))  # Builds on previous messages
```

### Conversation Manager Class

```python
class Conversation:
    """Manages a multi-turn conversation with Claude."""

    def __init__(self, system_prompt: str = None):
        self.client = Anthropic()
        self.system_prompt = system_prompt
        self.messages = []

    def send(self, user_input: str) -> str:
        """Send a message and return Claude's response."""
        self.messages.append({"role": "user", "content": user_input})

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=self.system_prompt or "",
            messages=self.messages
        )

        assistant_response = response.content[0].text
        self.messages.append({"role": "assistant", "content": assistant_response})

        return assistant_response

    def reset(self):
        """Clear conversation history."""
        self.messages = []

    def get_history(self) -> list:
        """Return the conversation history."""
        return self.messages.copy()
```

### With System Prompt

```python
conversation = Conversation(
    system_prompt="You are a Python tutor. Give concise explanations with examples."
)

response1 = conversation.send("What are list comprehensions?")
response2 = conversation.send("Can you show a more complex example?")
response3 = conversation.send("How do they compare to map()?")
```

---

## State Management Strategies

### 1. In-Memory (Simple Applications)

Store history in a list or object. Good for:
- CLI tools
- Single-user applications
- Short-lived sessions

### 2. Session Storage (Web Applications)

Store history in server sessions. Good for:
- Multi-user web apps
- Moderate conversation lengths
- Sessions that expire

```python
from flask import session

@app.route("/chat", methods=["POST"])
def chat():
    if "history" not in session:
        session["history"] = []

    history = session["history"]
    history.append({"role": "user", "content": request.json["message"]})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=history
    )

    assistant_msg = response.content[0].text
    history.append({"role": "assistant", "content": assistant_msg})
    session["history"] = history

    return {"response": assistant_msg}
```

### 3. Database Storage (Persistent Conversations)

Store history in a database. Good for:
- Conversations that span sessions
- Audit requirements
- Analytics and training data

---

## Best Practices

### 1. Handle Token Limits

As conversations grow, you may hit token limits. Strategies:

```python
def trim_history(messages: list, max_messages: int = 20) -> list:
    """Keep only the most recent messages."""
    if len(messages) > max_messages:
        return messages[-max_messages:]
    return messages
```

### 2. Summarize Long Conversations

For very long conversations, periodically summarize:

```python
def summarize_conversation(messages: list) -> str:
    """Create a summary of the conversation so far."""
    summary_request = messages + [{
        "role": "user",
        "content": "Please summarize our conversation so far in 2-3 sentences."
    }]

    response = client.messages.create(
        model="claude-3-5-haiku-20241022",  # Use Haiku for summaries
        max_tokens=200,
        messages=summary_request
    )

    return response.content[0].text
```

### 3. Include Relevant Context

Sometimes older context matters more than recent messages:

```python
def build_context_aware_history(
    recent_messages: list,
    important_context: list,
    max_tokens: int = 4000
) -> list:
    """Combine important context with recent messages."""
    # Always include important context first
    history = important_context.copy()

    # Add as many recent messages as fit
    for msg in reversed(recent_messages):
        history.append(msg)
        # Check token count and trim if needed

    return history
```

---

## Common Pitfalls

1. **Not storing assistant responses**: You must save Claude's responses to history
2. **Message ordering**: Keep strict user/assistant alternation
3. **Token overflow**: Monitor history length as conversations grow
4. **Losing context on page refresh**: Use persistent storage for web apps

---

## Exercises

1. **Chat Loop** (`exercises/01_chat_loop.py`): Build a simple CLI chatbot
2. **Conversation Persistence** (`exercises/02_persistence.py`): Save and load conversations
3. **Context Trimming** (`exercises/03_trimming.py`): Implement smart history trimming

---

## Next Steps

After completing this node, proceed to:
- [Context Window Management](../context-management/) - Optimize token usage
- [Streaming Responses](../streaming/) - Real-time response handling
