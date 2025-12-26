# Context Window Management

**Category:** Messaging
**Difficulty:** 4/5
**Estimated Time:** 60 minutes
**Prerequisites:** [Multi-turn Conversations](../multi-turn/)

---

## Learning Objectives

By the end of this node, you will:
- Understand token limits and context windows
- Implement strategies to optimize token usage
- Handle long conversations and large documents

---

## Concept Overview

Every Claude model has a **context window** - the maximum number of tokens it can process in a single request. This includes both input (your messages) and output (Claude's response).

### Context Window Sizes

| Model | Context Window |
|-------|----------------|
| Claude Opus 4 | 200,000 tokens |
| Claude Sonnet 4 | 200,000 tokens |
| Claude Haiku 3.5 | 200,000 tokens |

### Token Basics

- ~4 characters per token (English text)
- ~100 tokens per 75 words
- Code tends to use more tokens than prose
- Non-English text may use more tokens

---

## Key Patterns

### Counting Tokens

```python
from anthropic import Anthropic

client = Anthropic()

def count_tokens(text: str) -> int:
    """Count tokens in a text string using the API."""
    response = client.messages.count_tokens(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": text}]
    )
    return response.input_tokens


# Estimate without API call
def estimate_tokens(text: str) -> int:
    """Rough estimate: ~4 characters per token."""
    return len(text) // 4
```

### Truncating Long Inputs

```python
def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to approximately max_tokens."""
    # Rough estimate: 4 chars per token
    max_chars = max_tokens * 4

    if len(text) <= max_chars:
        return text

    # Truncate and add indicator
    truncated = text[:max_chars - 50]
    return truncated + "\n\n[Content truncated due to length]"
```

### Sliding Window for Conversations

```python
def sliding_window(
    messages: list,
    max_tokens: int = 50000,
    keep_first: int = 2
) -> list:
    """Keep recent messages within token budget, preserving first messages."""
    if len(messages) <= keep_first:
        return messages

    # Always keep the first N messages (often contain important context)
    preserved = messages[:keep_first]
    recent = messages[keep_first:]

    # Start from most recent, add until we hit the limit
    result = []
    current_tokens = sum(estimate_tokens(str(m)) for m in preserved)

    for msg in reversed(recent):
        msg_tokens = estimate_tokens(str(msg))
        if current_tokens + msg_tokens > max_tokens:
            break
        result.insert(0, msg)
        current_tokens += msg_tokens

    return preserved + result


def estimate_tokens(text: str) -> int:
    return len(text) // 4
```

### Summarization Strategy

```python
def summarize_and_continue(
    client: Anthropic,
    messages: list,
    summary_threshold: int = 30
) -> list:
    """When conversation gets long, summarize older messages."""
    if len(messages) < summary_threshold:
        return messages

    # Keep recent messages
    recent = messages[-10:]

    # Summarize older messages
    to_summarize = messages[:-10]
    summary_prompt = [{
        "role": "user",
        "content": f"""Summarize this conversation in 2-3 paragraphs, capturing:
- Main topics discussed
- Key decisions or conclusions
- Important context for continuing

Conversation:
{format_messages(to_summarize)}"""
    }]

    summary_response = client.messages.create(
        model="claude-3-5-haiku-20241022",  # Fast model for summarization
        max_tokens=500,
        messages=summary_prompt
    )

    summary = summary_response.content[0].text

    # Create new message list with summary
    return [
        {"role": "user", "content": f"[Previous conversation summary]\n{summary}"},
        {"role": "assistant", "content": "I understand. Let's continue from where we left off."},
    ] + recent


def format_messages(messages: list) -> str:
    """Format messages for display."""
    lines = []
    for msg in messages:
        role = msg["role"].upper()
        content = msg["content"][:500]  # Truncate for summary
        lines.append(f"{role}: {content}")
    return "\n\n".join(lines)
```

---

## Large Document Strategies

### 1. Chunking

Split large documents into manageable chunks:

```python
def chunk_document(
    text: str,
    chunk_size: int = 10000,
    overlap: int = 500
) -> list[str]:
    """Split document into overlapping chunks."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('. ')
            if last_period > chunk_size * 0.8:
                chunk = chunk[:last_period + 1]
                end = start + last_period + 1

        chunks.append(chunk)
        start = end - overlap

    return chunks
```

### 2. Map-Reduce for Analysis

Process chunks independently, then combine:

```python
def analyze_large_document(client: Anthropic, document: str) -> str:
    """Analyze a large document using map-reduce."""
    chunks = chunk_document(document, chunk_size=20000)

    # Map: Analyze each chunk
    chunk_analyses = []
    for i, chunk in enumerate(chunks):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"Analyze this section (part {i+1}/{len(chunks)}):\n\n{chunk}"
            }]
        )
        chunk_analyses.append(response.content[0].text)

    # Reduce: Combine analyses
    combined = "\n\n---\n\n".join(chunk_analyses)
    final_response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"Synthesize these section analyses into a coherent summary:\n\n{combined}"
        }]
    )

    return final_response.content[0].text
```

---

## Token Usage Optimization

### 1. Be Concise in System Prompts

```python
# Verbose (more tokens)
system = """You are a helpful assistant that helps users with their questions.
You should always be polite and professional. You should provide accurate
information and let users know when you're not sure about something..."""

# Concise (fewer tokens)
system = "Helpful assistant. Be accurate, concise, and professional."
```

### 2. Remove Redundant Context

Don't repeat information already in the conversation:

```python
# Instead of repeating context
bad_message = "Remember, we're building a Python web app using Flask. Now, about the database..."

# Reference existing context
good_message = "Now, about the database for our app..."
```

### 3. Use Efficient Prompting

```python
# Verbose
prompt = "Can you please explain to me in detail what a Python decorator is and how it works?"

# Efficient
prompt = "Explain Python decorators briefly."
```

---

## Common Pitfalls

1. **Ignoring token limits**: Always monitor usage as conversations grow
2. **Losing important context**: Don't discard critical early messages
3. **Inefficient summarization**: Use faster models for summaries
4. **Not chunking documents**: Large documents should be processed in parts

---

## Exercises

1. **Token Counter** (`exercises/01_token_counter.py`): Build a token counting utility
2. **Conversation Trimmer** (`exercises/02_trimmer.py`): Implement sliding window trimming
3. **Document Chunker** (`exercises/03_chunker.py`): Process a large document in chunks

---

## Next Steps

After completing this node, proceed to:
- [Streaming Responses](../streaming/) - Real-time response handling
- [Vision Capabilities](../vision/) - Process images and visual content
