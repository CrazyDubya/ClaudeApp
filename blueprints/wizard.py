#!/usr/bin/env python3
"""
Blueprint Selection Wizard

Interactive CLI wizard to help users choose and instantiate
the right blueprint for their use case.

Usage:
    python wizard.py              # Interactive mode
    python wizard.py --list       # List all blueprints
    python wizard.py --recommend  # Get recommendation based on questions
"""

import argparse
import os
import shutil
from pathlib import Path
from typing import Optional

import yaml


class BlueprintWizard:
    """Interactive blueprint selection and instantiation wizard."""

    def __init__(self):
        self.blueprints_dir = Path(__file__).parent
        self.registry = self._load_registry()

    def _load_registry(self) -> dict:
        """Load the blueprint registry."""
        registry_path = self.blueprints_dir / "registry.yaml"
        with open(registry_path) as f:
            return yaml.safe_load(f)

    def list_blueprints(self):
        """List all available blueprints."""
        print()
        print("=" * 60)
        print("AVAILABLE BLUEPRINTS")
        print("=" * 60)
        print()

        for bp_id, bp_info in self.registry.get("blueprints", {}).items():
            status = bp_info.get("status", "unknown")
            if status == "planned":
                continue  # Skip planned blueprints

            difficulty = bp_info.get("difficulty", "unknown")
            time = bp_info.get("implementation_time", "unknown")

            print(f"📦 {bp_info.get('name', bp_id)}")
            print(f"   ID: {bp_id}")
            print(f"   {bp_info.get('description', 'No description')}")
            print(f"   Difficulty: {difficulty} | Time: {time}")
            print(f"   Use cases: {', '.join(bp_info.get('use_cases', [])[:3])}")
            print()

    def recommend(self) -> Optional[str]:
        """Interactive recommendation based on user needs."""
        print()
        print("=" * 60)
        print("BLUEPRINT RECOMMENDATION WIZARD")
        print("=" * 60)
        print()
        print("Answer a few questions to find the right blueprint.")
        print()

        # Question 1: Primary interaction type
        print("1. What type of application are you building?")
        print("   a) Chat/conversation interface")
        print("   b) Document/data processing")
        print("   c) Autonomous task completion")
        print("   d) Not sure yet")
        print()

        q1 = input("Your choice (a/b/c/d): ").strip().lower()

        # Question 2: Complexity
        print()
        print("2. How complex is your use case?")
        print("   a) Simple - just want to get started")
        print("   b) Moderate - need some customization")
        print("   c) Complex - production-grade requirements")
        print()

        q2 = input("Your choice (a/b/c): ").strip().lower()

        # Question 3: Key feature
        print()
        print("3. What's most important to you?")
        print("   a) Real-time streaming responses")
        print("   b) Structured data extraction")
        print("   c) Multi-turn conversation memory")
        print("   d) Tool/function calling")
        print()

        q3 = input("Your choice (a/b/c/d): ").strip().lower()

        # Determine recommendation
        recommendation = self._analyze_answers(q1, q2, q3)

        print()
        print("=" * 60)
        print("RECOMMENDATION")
        print("=" * 60)
        print()

        if recommendation:
            bp_info = self.registry["blueprints"].get(recommendation, {})
            print(f"Based on your answers, we recommend:")
            print()
            print(f"📦 {bp_info.get('name', recommendation)}")
            print(f"   {bp_info.get('description', '')}")
            print()
            print(f"Difficulty: {bp_info.get('difficulty', 'unknown')}")
            print(f"Estimated time: {bp_info.get('implementation_time', 'unknown')}")
            print()
            print("To get started:")
            print(f"   1. Review the blueprint: blueprints/{recommendation}/README.md")
            print(f"   2. Complete prerequisites: {', '.join(bp_info.get('required_skills', []))}")
            print(f"   3. Run the wizard to create your project")
            print()

            proceed = input("Would you like to create a new project? (y/n): ").strip().lower()
            if proceed == "y":
                self.instantiate(recommendation)

            return recommendation
        else:
            print("We couldn't determine a specific recommendation.")
            print("Please review the available blueprints with --list")
            return None

    def _analyze_answers(self, q1: str, q2: str, q3: str) -> Optional[str]:
        """Analyze answers to determine recommendation."""
        # Scoring for each blueprint
        scores = {
            "conversational-assistant": 0,
            "document-processor": 0,
        }

        # Q1: Application type
        if q1 == "a":  # Chat/conversation
            scores["conversational-assistant"] += 3
        elif q1 == "b":  # Document processing
            scores["document-processor"] += 3
        elif q1 == "c":  # Autonomous tasks
            scores["document-processor"] += 1  # Agent blueprints not available yet

        # Q2: Complexity (both blueprints can handle any complexity)
        if q2 == "a":  # Simple
            scores["conversational-assistant"] += 1  # Easier to start with

        # Q3: Key feature
        if q3 == "a":  # Streaming
            scores["conversational-assistant"] += 2
        elif q3 == "b":  # Structured extraction
            scores["document-processor"] += 2
        elif q3 == "c":  # Multi-turn memory
            scores["conversational-assistant"] += 2
        elif q3 == "d":  # Tool calling
            scores["document-processor"] += 2

        # Return highest scoring blueprint
        if scores["conversational-assistant"] >= scores["document-processor"]:
            return "conversational-assistant"
        else:
            return "document-processor"

    def instantiate(self, blueprint_id: str, output_dir: Optional[str] = None):
        """Create a new project from a blueprint template."""
        bp_info = self.registry["blueprints"].get(blueprint_id)
        if not bp_info:
            print(f"Error: Blueprint '{blueprint_id}' not found")
            return

        templates_dir = self.blueprints_dir / blueprint_id / "templates"
        if not templates_dir.exists():
            print(f"Error: No templates found for '{blueprint_id}'")
            return

        # Get project name
        if not output_dir:
            print()
            default_name = f"my-{blueprint_id}"
            output_dir = input(f"Project name [{default_name}]: ").strip() or default_name

        output_path = Path(output_dir)

        if output_path.exists():
            print(f"Error: Directory '{output_dir}' already exists")
            return

        print()
        print(f"Creating project: {output_dir}")
        print()

        # Create directory structure
        output_path.mkdir(parents=True)
        (output_path / "src").mkdir()
        (output_path / "tests").mkdir()
        (output_path / "prompts").mkdir(exist_ok=True)

        # Copy templates
        for template_file in templates_dir.glob("*.template"):
            # Remove .template extension
            dest_name = template_file.stem
            dest_path = output_path / "src" / dest_name

            # Read and process template
            content = template_file.read_text()
            dest_path.write_text(content)
            print(f"  Created: src/{dest_name}")

        # Create additional files
        self._create_requirements(output_path, blueprint_id)
        self._create_readme(output_path, blueprint_id, bp_info)
        self._create_system_prompt(output_path, blueprint_id)

        print()
        print("=" * 60)
        print("PROJECT CREATED SUCCESSFULLY")
        print("=" * 60)
        print()
        print(f"Your new project is in: {output_path}")
        print()
        print("Next steps:")
        print(f"  1. cd {output_dir}")
        print("  2. pip install -r requirements.txt")
        print("  3. Set ANTHROPIC_API_KEY environment variable")
        print("  4. python src/main.py")
        print()

    def _create_requirements(self, output_path: Path, blueprint_id: str):
        """Create requirements.txt."""
        requirements = [
            "anthropic>=0.40.0",
        ]

        if blueprint_id == "conversational-assistant":
            requirements.extend([
                "# Optional for web API",
                "# fastapi",
                "# uvicorn",
            ])
        elif blueprint_id == "document-processor":
            requirements.extend([
                "pyyaml",
                "# Optional for PDF support",
                "# pypdf",
            ])

        (output_path / "requirements.txt").write_text("\n".join(requirements))
        print("  Created: requirements.txt")

    def _create_readme(self, output_path: Path, blueprint_id: str, bp_info: dict):
        """Create README.md."""
        readme = f"""# {output_path.name}

Generated from the `{blueprint_id}` blueprint.

## Description

{bp_info.get('description', '')}

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"
```

## Usage

```bash
python src/main.py
```

## Configuration

See `src/config.py` for configuration options.
Environment variables can be used to override defaults.

## Blueprint Reference

- Blueprint: `{blueprint_id}`
- Difficulty: {bp_info.get('difficulty', 'unknown')}
- Required skills: {', '.join(bp_info.get('required_skills', []))}

For more information, see the blueprint documentation.
"""
        (output_path / "README.md").write_text(readme)
        print("  Created: README.md")

    def _create_system_prompt(self, output_path: Path, blueprint_id: str):
        """Create default system prompt."""
        prompts = {
            "conversational-assistant": """You are a helpful AI assistant.

Be concise, accurate, and helpful in your responses.
If you're unsure about something, say so.
Maintain a friendly and professional tone.""",

            "document-processor": """You are an expert document analyst.

Extract information accurately and completely.
Use the provided tools to structure your output.
If information is not present, omit it rather than guessing.""",
        }

        prompt = prompts.get(blueprint_id, "You are a helpful assistant.")
        (output_path / "prompts" / "system.txt").write_text(prompt)
        print("  Created: prompts/system.txt")


def main():
    parser = argparse.ArgumentParser(description="Blueprint Selection Wizard")
    parser.add_argument("--list", "-l", action="store_true", help="List all blueprints")
    parser.add_argument("--recommend", "-r", action="store_true", help="Get recommendation")
    parser.add_argument("--create", "-c", help="Create project from blueprint ID")
    parser.add_argument("--output", "-o", help="Output directory for --create")

    args = parser.parse_args()

    wizard = BlueprintWizard()

    if args.list:
        wizard.list_blueprints()
    elif args.create:
        wizard.instantiate(args.create, args.output)
    elif args.recommend:
        wizard.recommend()
    else:
        # Default: show interactive menu
        print()
        print("=" * 60)
        print("CLAUDE APP FORGE - BLUEPRINT WIZARD")
        print("=" * 60)
        print()
        print("What would you like to do?")
        print()
        print("  1. List available blueprints")
        print("  2. Get a recommendation")
        print("  3. Create a new project")
        print("  4. Exit")
        print()

        choice = input("Your choice (1/2/3/4): ").strip()

        if choice == "1":
            wizard.list_blueprints()
        elif choice == "2":
            wizard.recommend()
        elif choice == "3":
            print()
            print("Available blueprints:")
            print("  - conversational-assistant")
            print("  - document-processor")
            print()
            bp_id = input("Blueprint ID: ").strip()
            if bp_id:
                wizard.instantiate(bp_id)
        elif choice == "4":
            print("Goodbye!")
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
