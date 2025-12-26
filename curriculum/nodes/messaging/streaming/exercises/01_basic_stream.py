"""
Exercise 1: Basic Streaming

Goal: Implement streaming responses for real-time output.

Instructions:
1. Create a streaming request
2. Process events as they arrive
3. Display text in real-time

Challenge:
- Add a progress indicator
- Handle stream interruptions gracefully
"""

import os
import sys


def basic_stream():
    """
    TODO: Implement basic streaming.

    Use client.messages.stream() to get real-time responses.
    Process each text chunk as it arrives.
    """
    from anthropic import Anthropic

    client = Anthropic()

    print("Streaming response:\n")

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": "Write a short poem about coding, line by line.",
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print("\n")  # Final newline


def stream_with_stats():
    """
    TODO: Stream with statistics tracking.

    Track:
    - Number of chunks received
    - Total characters
    - Time to first token
    - Total time
    """
    import time
    from anthropic import Anthropic

    client = Anthropic()

    stats = {
        "chunks": 0,
        "chars": 0,
        "start_time": time.time(),
        "first_token_time": None,
    }

    print("Streaming with stats:\n")

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": "Explain recursion briefly."}],
    ) as stream:
        for text in stream.text_stream:
            if stats["first_token_time"] is None:
                stats["first_token_time"] = time.time()

            stats["chunks"] += 1
            stats["chars"] += len(text)
            print(text, end="", flush=True)

    end_time = time.time()

    print("\n\n--- Statistics ---")
    print(f"Chunks received: {stats['chunks']}")
    print(f"Total characters: {stats['chars']}")
    if stats["first_token_time"]:
        ttft = (stats["first_token_time"] - stats["start_time"]) * 1000
        print(f"Time to first token: {ttft:.0f}ms")
    print(f"Total time: {(end_time - stats['start_time']) * 1000:.0f}ms")


def stream_with_callback(callback):
    """
    TODO: Implement streaming with a callback function.

    The callback receives each text chunk as it arrives.
    Useful for updating UIs or processing in real-time.
    """
    from anthropic import Anthropic

    client = Anthropic()

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=150,
        messages=[{"role": "user", "content": "Count from 1 to 5 slowly."}],
    ) as stream:
        for text in stream.text_stream:
            callback(text)


def main():
    print("=" * 50)
    print("Exercise 1: Basic Streaming")
    print("=" * 50)

    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("\nValidation mode - skipping API calls")
        print("This exercise demonstrates streaming responses")
        return

    print("\n1. Basic streaming:")
    basic_stream()

    print("\n2. Streaming with statistics:")
    stream_with_stats()

    print("\n3. Streaming with callback:")

    def my_callback(text):
        # Custom processing - uppercase everything
        sys.stdout.write(text.upper())
        sys.stdout.flush()

    stream_with_callback(my_callback)
    print("\n")


if __name__ == "__main__":
    main()
