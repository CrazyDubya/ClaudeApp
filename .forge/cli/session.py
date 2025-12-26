#!/usr/bin/env python3
"""
Claude App Forge - Session Manager

Save and resume learning sessions. Sessions track:
- Current node being studied
- Time spent on each node
- Notes and bookmarks
- Exercise progress

Usage:
    python session.py                    # Show current session
    python session.py --start node-id    # Start studying a node
    python session.py --pause            # Pause current session
    python session.py --resume           # Resume last session
    python session.py --history          # Show session history
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import yaml


class Colors:
    """ANSI color codes."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    END = "\033[0m"


class SessionManager:
    """Manages learning sessions with save/resume capability."""

    def __init__(self, forge_root: Path, journal_name: str = "my-journal"):
        self.forge_root = forge_root
        self.journal_name = journal_name
        self.sessions_dir = forge_root / "journals" / journal_name / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_file = self.sessions_dir / "current.json"
        self.history_file = self.sessions_dir / "history.json"

    def _load_current_session(self) -> Optional[dict]:
        """Load the current active session."""
        if self.current_session_file.exists():
            try:
                with open(self.current_session_file) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return None

    def _save_current_session(self, session: dict):
        """Save the current session."""
        with open(self.current_session_file, "w") as f:
            json.dump(session, f, indent=2)

    def _load_history(self) -> list:
        """Load session history."""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return []

    def _save_history(self, history: list):
        """Save session history."""
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2)

    def _get_node_info(self, node_id: str) -> Optional[dict]:
        """Get information about a curriculum node."""
        graph_path = self.forge_root / "curriculum" / "graph.yaml"
        if not graph_path.exists():
            return None

        with open(graph_path) as f:
            graph = yaml.safe_load(f)

        return graph.get("nodes", {}).get(node_id)

    def _find_node_path(self, node_id: str) -> Optional[Path]:
        """Find the path to a node's directory."""
        nodes_dir = self.forge_root / "curriculum" / "nodes"
        for category_dir in nodes_dir.iterdir():
            if category_dir.is_dir():
                node_path = category_dir / node_id
                if node_path.exists():
                    return node_path
        return None

    def start(self, node_id: str) -> bool:
        """Start a new study session for a node."""
        # Check if node exists
        node_info = self._get_node_info(node_id)
        if not node_info:
            print(f"{Colors.RED}✗{Colors.END} Node '{node_id}' not found in curriculum")
            return False

        # Pause any existing session
        current = self._load_current_session()
        if current and current.get("status") == "active":
            self._pause_session(current)

        # Create new session
        session = {
            "node_id": node_id,
            "node_name": node_info.get("name", node_id),
            "started_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "status": "active",
            "time_spent_minutes": 0,
            "notes": [],
            "bookmarks": [],
            "exercises_completed": [],
        }

        self._save_current_session(session)

        print()
        print(f"{Colors.GREEN}✓{Colors.END} Session started: {Colors.BOLD}{node_info.get('name', node_id)}{Colors.END}")
        print()
        print(f"  Difficulty: {'★' * node_info.get('difficulty', 1)}{'☆' * (5 - node_info.get('difficulty', 1))}")
        print(f"  Estimated time: {node_info.get('estimated_time', 'unknown')}")
        print()

        # Show what to study
        node_path = self._find_node_path(node_id)
        if node_path:
            readme = node_path / "README.md"
            if readme.exists():
                print(f"  Start here: {readme.relative_to(self.forge_root)}")

            examples_dir = node_path / "examples"
            if examples_dir.exists():
                examples = list(examples_dir.glob("*.py"))
                if examples:
                    print(f"  Examples: {len(examples)} files in {examples_dir.relative_to(self.forge_root)}/")

            exercises_dir = node_path / "exercises"
            if exercises_dir.exists():
                exercises = list(exercises_dir.glob("*.py"))
                if exercises:
                    print(f"  Exercises: {len(exercises)} files in {exercises_dir.relative_to(self.forge_root)}/")

        print()
        print(f"  Use 'python session.py --pause' when you take a break")
        print(f"  Use 'python session.py --note \"your note\"' to add notes")
        print()

        return True

    def _pause_session(self, session: dict):
        """Pause a session and calculate time spent."""
        if session.get("status") != "active":
            return

        # Calculate time spent
        last_activity = datetime.fromisoformat(session["last_activity"])
        elapsed = datetime.now() - last_activity
        session["time_spent_minutes"] += int(elapsed.total_seconds() / 60)
        session["status"] = "paused"
        session["paused_at"] = datetime.now().isoformat()

        self._save_current_session(session)

    def pause(self) -> bool:
        """Pause the current session."""
        session = self._load_current_session()
        if not session:
            print(f"{Colors.YELLOW}⚠{Colors.END} No active session to pause")
            return False

        if session.get("status") != "active":
            print(f"{Colors.YELLOW}⚠{Colors.END} Session already paused")
            return False

        self._pause_session(session)

        print()
        print(f"{Colors.YELLOW}⏸{Colors.END} Session paused: {Colors.BOLD}{session['node_name']}{Colors.END}")
        print(f"  Time spent: {session['time_spent_minutes']} minutes")
        print()
        print(f"  Use 'python session.py --resume' to continue")
        print()

        return True

    def resume(self) -> bool:
        """Resume the paused session."""
        session = self._load_current_session()
        if not session:
            print(f"{Colors.YELLOW}⚠{Colors.END} No session to resume")
            print("  Use 'python session.py --start <node-id>' to start a new session")
            return False

        if session.get("status") == "active":
            print(f"{Colors.GREEN}✓{Colors.END} Session already active: {session['node_name']}")
            return True

        # Resume
        session["status"] = "active"
        session["last_activity"] = datetime.now().isoformat()
        del session["paused_at"]

        self._save_current_session(session)

        print()
        print(f"{Colors.GREEN}▶{Colors.END} Session resumed: {Colors.BOLD}{session['node_name']}{Colors.END}")
        print(f"  Total time: {session['time_spent_minutes']} minutes")
        print()

        return True

    def complete(self) -> bool:
        """Mark current session as complete."""
        session = self._load_current_session()
        if not session:
            print(f"{Colors.YELLOW}⚠{Colors.END} No active session")
            return False

        # Calculate final time
        if session.get("status") == "active":
            last_activity = datetime.fromisoformat(session["last_activity"])
            elapsed = datetime.now() - last_activity
            session["time_spent_minutes"] += int(elapsed.total_seconds() / 60)

        session["status"] = "completed"
        session["completed_at"] = datetime.now().isoformat()

        # Add to history
        history = self._load_history()
        history.append(session)
        self._save_history(history)

        # Clear current session
        self.current_session_file.unlink()

        print()
        print(f"{Colors.GREEN}🎉 Session complete: {session['node_name']}{Colors.END}")
        print(f"  Time spent: {session['time_spent_minutes']} minutes")
        print(f"  Notes: {len(session.get('notes', []))}")
        print(f"  Exercises: {len(session.get('exercises_completed', []))}")
        print()

        # Suggest next steps
        node_info = self._get_node_info(session["node_id"])
        if node_info:
            next_nodes = node_info.get("unlocks", [])
            if next_nodes:
                print(f"  Next up: {', '.join(next_nodes)}")
                print(f"  Start with: python session.py --start {next_nodes[0]}")
                print()

        return True

    def add_note(self, note: str) -> bool:
        """Add a note to the current session."""
        session = self._load_current_session()
        if not session:
            print(f"{Colors.YELLOW}⚠{Colors.END} No active session")
            return False

        session["notes"].append({
            "timestamp": datetime.now().isoformat(),
            "text": note,
        })
        session["last_activity"] = datetime.now().isoformat()
        self._save_current_session(session)

        print(f"{Colors.GREEN}✓{Colors.END} Note added")
        return True

    def add_bookmark(self, file_path: str, line: Optional[int] = None) -> bool:
        """Add a bookmark to the current session."""
        session = self._load_current_session()
        if not session:
            print(f"{Colors.YELLOW}⚠{Colors.END} No active session")
            return False

        session["bookmarks"].append({
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "line": line,
        })
        session["last_activity"] = datetime.now().isoformat()
        self._save_current_session(session)

        print(f"{Colors.GREEN}✓{Colors.END} Bookmark added: {file_path}")
        return True

    def mark_exercise(self, exercise_name: str) -> bool:
        """Mark an exercise as completed."""
        session = self._load_current_session()
        if not session:
            print(f"{Colors.YELLOW}⚠{Colors.END} No active session")
            return False

        if exercise_name not in session["exercises_completed"]:
            session["exercises_completed"].append(exercise_name)
            session["last_activity"] = datetime.now().isoformat()
            self._save_current_session(session)
            print(f"{Colors.GREEN}✓{Colors.END} Exercise completed: {exercise_name}")
        else:
            print(f"{Colors.YELLOW}⚠{Colors.END} Already completed: {exercise_name}")

        return True

    def show_current(self):
        """Show current session status."""
        session = self._load_current_session()

        print()
        print(f"{Colors.BOLD}Current Session{Colors.END}")
        print("=" * 50)

        if not session:
            print()
            print(f"  {Colors.GRAY}No active session{Colors.END}")
            print()
            print("  Start one with: python session.py --start <node-id>")
            print("  List nodes with: python .forge/cli/progress.py --detailed")
            print()
            return

        # Calculate current time
        time_spent = session["time_spent_minutes"]
        if session.get("status") == "active":
            last_activity = datetime.fromisoformat(session["last_activity"])
            elapsed = datetime.now() - last_activity
            time_spent += int(elapsed.total_seconds() / 60)

        status_icon = {
            "active": f"{Colors.GREEN}●{Colors.END}",
            "paused": f"{Colors.YELLOW}⏸{Colors.END}",
            "completed": f"{Colors.GREEN}✓{Colors.END}",
        }.get(session.get("status", "unknown"), "○")

        print()
        print(f"  {status_icon} {Colors.BOLD}{session['node_name']}{Colors.END}")
        print(f"  Status: {session.get('status', 'unknown')}")
        print(f"  Time spent: {time_spent} minutes")
        print(f"  Started: {session['started_at'][:16]}")
        print()

        # Notes
        notes = session.get("notes", [])
        if notes:
            print(f"  {Colors.BOLD}Notes ({len(notes)}):{Colors.END}")
            for note in notes[-3:]:  # Show last 3
                print(f"    • {note['text'][:60]}...")
            print()

        # Bookmarks
        bookmarks = session.get("bookmarks", [])
        if bookmarks:
            print(f"  {Colors.BOLD}Bookmarks ({len(bookmarks)}):{Colors.END}")
            for bm in bookmarks[-3:]:
                line_info = f":{bm['line']}" if bm.get("line") else ""
                print(f"    📍 {bm['file']}{line_info}")
            print()

        # Exercises
        exercises = session.get("exercises_completed", [])
        if exercises:
            print(f"  {Colors.BOLD}Exercises completed:{Colors.END} {len(exercises)}")
            print()

        # Actions
        print(f"  {Colors.GRAY}Actions:{Colors.END}")
        if session.get("status") == "active":
            print("    --pause     Pause session")
            print("    --complete  Mark as complete")
        else:
            print("    --resume    Resume session")
        print("    --note      Add a note")
        print()

    def show_history(self, limit: int = 10):
        """Show session history."""
        history = self._load_history()

        print()
        print(f"{Colors.BOLD}Session History{Colors.END}")
        print("=" * 50)

        if not history:
            print()
            print(f"  {Colors.GRAY}No completed sessions yet{Colors.END}")
            print()
            return

        print()
        for session in reversed(history[-limit:]):
            completed = session.get("completed_at", "")[:10]
            print(f"  {Colors.GREEN}✓{Colors.END} {session['node_name']}")
            print(f"    Completed: {completed} | Time: {session['time_spent_minutes']} min")

        print()
        total_time = sum(s.get("time_spent_minutes", 0) for s in history)
        print(f"  {Colors.BOLD}Total: {len(history)} sessions, {total_time} minutes{Colors.END}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Manage learning sessions")
    parser.add_argument("--start", metavar="NODE", help="Start studying a node")
    parser.add_argument("--pause", action="store_true", help="Pause current session")
    parser.add_argument("--resume", action="store_true", help="Resume paused session")
    parser.add_argument("--complete", action="store_true", help="Mark session as complete")
    parser.add_argument("--note", metavar="TEXT", help="Add a note to current session")
    parser.add_argument("--bookmark", metavar="FILE", help="Bookmark a file")
    parser.add_argument("--exercise", metavar="NAME", help="Mark exercise as done")
    parser.add_argument("--history", action="store_true", help="Show session history")
    parser.add_argument("--journal", default="my-journal", help="Journal name")

    args = parser.parse_args()

    forge_root = Path(__file__).parent.parent.parent
    manager = SessionManager(forge_root, args.journal)

    if args.start:
        manager.start(args.start)
    elif args.pause:
        manager.pause()
    elif args.resume:
        manager.resume()
    elif args.complete:
        manager.complete()
    elif args.note:
        manager.add_note(args.note)
    elif args.bookmark:
        manager.add_bookmark(args.bookmark)
    elif args.exercise:
        manager.mark_exercise(args.exercise)
    elif args.history:
        manager.show_history()
    else:
        manager.show_current()


if __name__ == "__main__":
    main()
