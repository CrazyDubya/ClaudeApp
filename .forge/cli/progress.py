#!/usr/bin/env python3
"""
Claude App Forge - Progress Tracker

Track your learning progress through the curriculum.
Shows completed nodes, current position, and recommended next steps.

Usage:
    python progress.py                  # Show overall progress
    python progress.py --path chatbot   # Show path-specific progress
    python progress.py --complete node  # Mark a node as complete
    python progress.py --reset          # Reset all progress
"""

import argparse
import json
from datetime import datetime
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


# Learning paths with their required nodes
LEARNING_PATHS = {
    "quick-start": {
        "name": "Quick Start",
        "nodes": ["sdk-setup", "api-keys", "first-message"],
        "description": "Get started with Claude SDK",
    },
    "chatbot": {
        "name": "Chatbot Developer",
        "nodes": [
            "sdk-setup", "api-keys", "first-message",
            "message-structure", "system-prompts", "streaming", "multi-turn"
        ],
        "description": "Build conversational applications",
    },
    "document": {
        "name": "Document Processor",
        "nodes": [
            "sdk-setup", "api-keys", "first-message",
            "message-structure", "system-prompts", "vision", "context-management"
        ],
        "description": "Process and analyze documents",
    },
}


class ProgressTracker:
    """Tracks learning progress through the curriculum."""

    def __init__(self, forge_root: Path, journal_name: str = "my-journal"):
        self.forge_root = forge_root
        self.journal_name = journal_name
        self.progress_file = forge_root / "journals" / journal_name / "progress.json"
        self.progress = self._load_progress()

    def _load_progress(self) -> dict:
        """Load progress from file."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass

        return {
            "completed_nodes": [],
            "current_path": None,
            "started_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
        }

    def _save_progress(self):
        """Save progress to file."""
        self.progress["last_activity"] = datetime.now().isoformat()
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.progress_file, "w") as f:
            json.dump(self.progress, f, indent=2)

    def get_all_nodes(self) -> dict:
        """Get all curriculum nodes organized by category."""
        graph_path = self.forge_root / "curriculum" / "graph.yaml"
        if not graph_path.exists():
            return {}

        with open(graph_path) as f:
            graph = yaml.safe_load(f)

        nodes_by_category = {}
        for node_id, node_info in graph.get("nodes", {}).items():
            category = node_info.get("category", "other")
            if category not in nodes_by_category:
                nodes_by_category[category] = []
            nodes_by_category[category].append({
                "id": node_id,
                "name": node_info.get("name", node_id),
                "difficulty": node_info.get("difficulty", 1),
                "time": node_info.get("estimated_time", "unknown"),
            })

        return nodes_by_category

    def is_complete(self, node_id: str) -> bool:
        """Check if a node is complete."""
        return node_id in self.progress.get("completed_nodes", [])

    def mark_complete(self, node_id: str):
        """Mark a node as complete."""
        if node_id not in self.progress["completed_nodes"]:
            self.progress["completed_nodes"].append(node_id)
            self._save_progress()
            print(f"{Colors.GREEN}✓{Colors.END} Marked '{node_id}' as complete")

    def mark_incomplete(self, node_id: str):
        """Mark a node as incomplete."""
        if node_id in self.progress["completed_nodes"]:
            self.progress["completed_nodes"].remove(node_id)
            self._save_progress()
            print(f"  Marked '{node_id}' as incomplete")

    def set_path(self, path_id: str):
        """Set the current learning path."""
        if path_id in LEARNING_PATHS:
            self.progress["current_path"] = path_id
            self._save_progress()
            print(f"{Colors.GREEN}✓{Colors.END} Set path to: {LEARNING_PATHS[path_id]['name']}")
        else:
            print(f"{Colors.RED}✗{Colors.END} Unknown path: {path_id}")

    def reset(self):
        """Reset all progress."""
        self.progress = {
            "completed_nodes": [],
            "current_path": None,
            "started_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
        }
        self._save_progress()
        print(f"{Colors.YELLOW}⚠{Colors.END} Progress reset")

    def show_overall(self):
        """Show overall progress."""
        nodes = self.get_all_nodes()
        completed = set(self.progress.get("completed_nodes", []))

        print()
        print(f"{Colors.BOLD}Claude App Forge - Learning Progress{Colors.END}")
        print("=" * 50)
        print()

        # Current path
        current_path = self.progress.get("current_path")
        if current_path and current_path in LEARNING_PATHS:
            path_info = LEARNING_PATHS[current_path]
            print(f"Current Path: {Colors.BLUE}{path_info['name']}{Colors.END}")
            print()

        # Progress by category
        total_nodes = 0
        total_complete = 0

        for category, category_nodes in sorted(nodes.items()):
            cat_complete = sum(1 for n in category_nodes if n["id"] in completed)
            cat_total = len(category_nodes)
            total_nodes += cat_total
            total_complete += cat_complete

            # Progress bar
            bar_width = 20
            filled = int(bar_width * cat_complete / cat_total) if cat_total > 0 else 0
            bar = "█" * filled + "░" * (bar_width - filled)

            color = Colors.GREEN if cat_complete == cat_total else (
                Colors.YELLOW if cat_complete > 0 else Colors.GRAY
            )

            print(f"  {category.capitalize():<15} [{bar}] {cat_complete}/{cat_total}")

        # Overall
        print()
        overall_pct = (total_complete / total_nodes * 100) if total_nodes > 0 else 0
        print(f"  {Colors.BOLD}Overall: {total_complete}/{total_nodes} ({overall_pct:.0f}%){Colors.END}")

        # Next recommended
        print()
        self._show_recommended_next(completed)

    def show_path_progress(self, path_id: str):
        """Show progress for a specific learning path."""
        if path_id not in LEARNING_PATHS:
            print(f"{Colors.RED}✗{Colors.END} Unknown path: {path_id}")
            print("Available paths:", ", ".join(LEARNING_PATHS.keys()))
            return

        path = LEARNING_PATHS[path_id]
        completed = set(self.progress.get("completed_nodes", []))

        print()
        print(f"{Colors.BOLD}{path['name']}{Colors.END}")
        print(f"{path['description']}")
        print("=" * 50)
        print()

        for i, node_id in enumerate(path["nodes"], 1):
            if node_id in completed:
                status = f"{Colors.GREEN}✓{Colors.END}"
            elif i == 1 or path["nodes"][i-2] in completed:
                status = f"{Colors.YELLOW}→{Colors.END}"  # Current
            else:
                status = f"{Colors.GRAY}○{Colors.END}"

            print(f"  {status} {i}. {node_id}")

        # Summary
        path_complete = sum(1 for n in path["nodes"] if n in completed)
        path_total = len(path["nodes"])
        print()
        print(f"  Progress: {path_complete}/{path_total}")

        if path_complete == path_total:
            print(f"\n  {Colors.GREEN}🎉 Path Complete!{Colors.END}")

    def show_detailed(self):
        """Show detailed node-by-node progress."""
        nodes = self.get_all_nodes()
        completed = set(self.progress.get("completed_nodes", []))

        print()
        print(f"{Colors.BOLD}Detailed Progress{Colors.END}")
        print("=" * 50)

        for category, category_nodes in sorted(nodes.items()):
            print(f"\n{Colors.BOLD}{category.capitalize()}{Colors.END}")

            for node in sorted(category_nodes, key=lambda x: x["difficulty"]):
                if node["id"] in completed:
                    status = f"{Colors.GREEN}✓{Colors.END}"
                else:
                    status = f"{Colors.GRAY}○{Colors.END}"

                diff_stars = "★" * node["difficulty"] + "☆" * (5 - node["difficulty"])
                print(f"  {status} {node['name']:<25} {diff_stars} ({node['time']})")

    def _show_recommended_next(self, completed: set):
        """Show recommended next nodes."""
        current_path = self.progress.get("current_path")

        if current_path and current_path in LEARNING_PATHS:
            path = LEARNING_PATHS[current_path]
            for node_id in path["nodes"]:
                if node_id not in completed:
                    print(f"{Colors.BOLD}Next Step:{Colors.END}")
                    print(f"  → Study: curriculum/nodes/*/{node_id}/README.md")
                    return

            print(f"{Colors.GREEN}Path complete! Consider trying another path.{Colors.END}")
        else:
            # Suggest based on dependencies
            print(f"{Colors.BOLD}Suggested:{Colors.END}")
            if "sdk-setup" not in completed:
                print("  → Start with: sdk-setup")
            elif "first-message" not in completed:
                print("  → Try: first-message")
            else:
                print("  → Explore the curriculum or choose a learning path")


def main():
    parser = argparse.ArgumentParser(description="Track learning progress")
    parser.add_argument("--path", help="Show progress for a specific path")
    parser.add_argument("--complete", metavar="NODE", help="Mark a node as complete")
    parser.add_argument("--uncomplete", metavar="NODE", help="Mark a node as incomplete")
    parser.add_argument("--set-path", metavar="PATH", help="Set current learning path")
    parser.add_argument("--detailed", action="store_true", help="Show detailed progress")
    parser.add_argument("--reset", action="store_true", help="Reset all progress")
    parser.add_argument("--journal", default="my-journal", help="Journal name")

    args = parser.parse_args()

    forge_root = Path(__file__).parent.parent.parent
    tracker = ProgressTracker(forge_root, args.journal)

    if args.reset:
        if input("Reset all progress? (yes/no): ").strip().lower() == "yes":
            tracker.reset()
    elif args.complete:
        tracker.mark_complete(args.complete)
    elif args.uncomplete:
        tracker.mark_incomplete(args.uncomplete)
    elif args.set_path:
        tracker.set_path(args.set_path)
    elif args.path:
        tracker.show_path_progress(args.path)
    elif args.detailed:
        tracker.show_detailed()
    else:
        tracker.show_overall()


if __name__ == "__main__":
    main()
