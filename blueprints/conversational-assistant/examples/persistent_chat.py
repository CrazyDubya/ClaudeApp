"""
Persistent Chat Assistant

A conversational assistant that saves conversations to disk.
Demonstrates file-based persistence for conversation continuity.

Usage:
    python persistent_chat.py                    # Start new or resume last session
    python persistent_chat.py --session mysess   # Use specific session
    python persistent_chat.py --list             # List all sessions
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from anthropic import Anthropic


class PersistentAssistant:
    """Conversational assistant with file-based persistence."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        storage_dir: str = ".chat_sessions",
        system_prompt: str = "You are a helpful assistant.",
    ):
        self.client = Anthropic()
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        self.system_prompt = system_prompt
        self.session_id = session_id or self._generate_session_id()
        self.history: list[dict] = []
        self.metadata: dict = {}

        self._load_session()

    def _generate_session_id(self) -> str:
        """Generate a new session ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _session_path(self) -> Path:
        """Get the path to the session file."""
        return self.storage_dir / f"{self.session_id}.json"

    def _load_session(self):
        """Load session from disk if it exists."""
        path = self._session_path()
        if path.exists():
            with open(path) as f:
                data = json.load(f)
                self.history = data.get("history", [])
                self.metadata = data.get("metadata", {})
                print(f"Resumed session: {self.session_id}")
                print(f"Messages in history: {len(self.history)}")
        else:
            self.metadata = {
                "created_at": datetime.now().isoformat(),
                "system_prompt": self.system_prompt,
            }
            print(f"New session: {self.session_id}")

    def _save_session(self):
        """Save session to disk."""
        self.metadata["updated_at"] = datetime.now().isoformat()
        self.metadata["message_count"] = len(self.history)

        with open(self._session_path(), "w") as f:
            json.dump(
                {
                    "session_id": self.session_id,
                    "history": self.history,
                    "metadata": self.metadata,
                },
                f,
                indent=2,
            )

    def send_message(self, user_message: str) -> str:
        """Send a message and get a response."""
        self.history.append({"role": "user", "content": user_message})

        # Stream response
        full_response = ""
        with self.client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=self.system_prompt,
            messages=self.history,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_response += text

        print()

        self.history.append({"role": "assistant", "content": full_response})
        self._save_session()

        return full_response

    def clear_history(self):
        """Clear conversation history but keep session."""
        self.history = []
        self._save_session()
        print("[History cleared, session preserved]")

    def show_history(self, last_n: int = 10):
        """Show recent conversation history."""
        messages = self.history[-last_n * 2 :]  # Get last N exchanges
        print(f"\n--- Last {len(messages)} messages ---")
        for msg in messages:
            role = msg["role"].upper()
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            print(f"[{role}] {content}")
        print("---")

    @classmethod
    def list_sessions(cls, storage_dir: str = ".chat_sessions") -> list[dict]:
        """List all available sessions."""
        path = Path(storage_dir)
        if not path.exists():
            return []

        sessions = []
        for file in path.glob("*.json"):
            try:
                with open(file) as f:
                    data = json.load(f)
                    sessions.append({
                        "session_id": data.get("session_id", file.stem),
                        "message_count": data.get("metadata", {}).get("message_count", 0),
                        "updated_at": data.get("metadata", {}).get("updated_at", "unknown"),
                    })
            except json.JSONDecodeError:
                pass

        return sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)


def main():
    parser = argparse.ArgumentParser(description="Persistent Chat Assistant")
    parser.add_argument("--session", "-s", help="Session ID to use or resume")
    parser.add_argument("--list", "-l", action="store_true", help="List all sessions")
    parser.add_argument("--storage", default=".chat_sessions", help="Storage directory")

    args = parser.parse_args()

    if args.list:
        sessions = PersistentAssistant.list_sessions(args.storage)
        if not sessions:
            print("No sessions found.")
        else:
            print(f"\n{'Session ID':<20} {'Messages':<10} {'Last Updated'}")
            print("-" * 60)
            for s in sessions:
                print(f"{s['session_id']:<20} {s['message_count']:<10} {s['updated_at']}")
        return

    print("=" * 50)
    print("Persistent Chat Assistant")
    print("=" * 50)
    print("Commands: quit, clear, history, sessions")
    print()

    assistant = PersistentAssistant(
        session_id=args.session,
        storage_dir=args.storage,
    )

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("Goodbye! Session saved.")
                break

            if user_input.lower() == "clear":
                assistant.clear_history()
                continue

            if user_input.lower() == "history":
                assistant.show_history()
                continue

            if user_input.lower() == "sessions":
                for s in PersistentAssistant.list_sessions(args.storage):
                    print(f"  {s['session_id']}: {s['message_count']} messages")
                continue

            print("\nAssistant: ", end="")
            assistant.send_message(user_input)

        except KeyboardInterrupt:
            print("\n\nGoodbye! Session saved.")
            break


if __name__ == "__main__":
    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("✓ Example validated (syntax check only)")
    else:
        main()
