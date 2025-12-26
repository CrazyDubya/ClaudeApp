#!/usr/bin/env python3
"""
Claude App Forge - Interactive Setup Wizard

Guides new users through the initial setup process:
- Checking prerequisites (Python, SDK)
- Setting up API key
- Creating initial journal
- Recommending a learning path

Usage:
    python setup_wizard.py           # Full interactive setup
    python setup_wizard.py --check   # Just check prerequisites
    python setup_wizard.py --quick   # Quick setup with defaults
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"

    @classmethod
    def disable(cls):
        """Disable colors for non-TTY output."""
        cls.GREEN = cls.YELLOW = cls.RED = cls.BLUE = cls.BOLD = cls.END = ""


class SetupWizard:
    """Interactive setup wizard for Claude App Forge."""

    def __init__(self, forge_root: Path):
        self.forge_root = forge_root
        self.config = {}

        # Disable colors if not a TTY
        if not sys.stdout.isatty():
            Colors.disable()

    def run(self, quick: bool = False) -> bool:
        """Run the complete setup wizard."""
        self._print_header()

        # Step 1: Check prerequisites
        print(f"\n{Colors.BOLD}Step 1: Checking Prerequisites{Colors.END}")
        print("-" * 40)
        prereqs_ok = self._check_prerequisites()
        if not prereqs_ok:
            return False

        # Step 2: API Key setup
        print(f"\n{Colors.BOLD}Step 2: API Key Configuration{Colors.END}")
        print("-" * 40)
        api_ok = self._setup_api_key(quick)
        if not api_ok:
            print(f"{Colors.YELLOW}⚠ API key not configured. You can set it later.{Colors.END}")

        # Step 3: Create journal
        print(f"\n{Colors.BOLD}Step 3: Create Your Journal{Colors.END}")
        print("-" * 40)
        self._setup_journal(quick)

        # Step 4: Choose learning path
        print(f"\n{Colors.BOLD}Step 4: Choose Your Path{Colors.END}")
        print("-" * 40)
        self._choose_learning_path(quick)

        # Step 5: Summary
        self._print_summary()

        return True

    def _print_header(self):
        """Print the welcome header."""
        print()
        print(f"{Colors.BOLD}{'=' * 50}{Colors.END}")
        print(f"{Colors.BOLD}   Claude App Forge - Setup Wizard{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 50}{Colors.END}")
        print()
        print("Welcome! This wizard will help you get started.")
        print("Press Ctrl+C at any time to exit.")

    def _check_prerequisites(self) -> bool:
        """Check all prerequisites are met."""
        all_ok = True

        # Check Python version
        py_version = sys.version_info
        if py_version >= (3, 8):
            print(f"  {Colors.GREEN}✓{Colors.END} Python {py_version.major}.{py_version.minor}.{py_version.micro}")
        else:
            print(f"  {Colors.RED}✗{Colors.END} Python 3.8+ required (found {py_version.major}.{py_version.minor})")
            all_ok = False

        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"],
                         capture_output=True, check=True)
            print(f"  {Colors.GREEN}✓{Colors.END} pip available")
        except subprocess.CalledProcessError:
            print(f"  {Colors.RED}✗{Colors.END} pip not available")
            all_ok = False

        # Check anthropic SDK
        try:
            import anthropic
            print(f"  {Colors.GREEN}✓{Colors.END} anthropic SDK v{anthropic.__version__}")
        except ImportError:
            print(f"  {Colors.YELLOW}○{Colors.END} anthropic SDK not installed")
            if self._prompt_yes_no("  Install it now?"):
                self._install_sdk()
            else:
                all_ok = False

        # Check git (optional)
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  {Colors.GREEN}✓{Colors.END} git available")
        except FileNotFoundError:
            print(f"  {Colors.YELLOW}○{Colors.END} git not found (optional)")

        return all_ok

    def _install_sdk(self):
        """Install the Anthropic SDK."""
        print("  Installing anthropic SDK...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "anthropic", "-q"],
                check=True
            )
            print(f"  {Colors.GREEN}✓{Colors.END} anthropic SDK installed")
        except subprocess.CalledProcessError:
            print(f"  {Colors.RED}✗{Colors.END} Failed to install SDK")

    def _setup_api_key(self, quick: bool) -> bool:
        """Set up the API key."""
        # Check if already set
        existing_key = os.environ.get("ANTHROPIC_API_KEY")
        if existing_key:
            masked = f"{existing_key[:7]}...{existing_key[-4:]}" if len(existing_key) > 15 else "***"
            print(f"  {Colors.GREEN}✓{Colors.END} API key already configured: {masked}")
            return True

        if quick:
            print(f"  {Colors.YELLOW}○{Colors.END} API key not set (set ANTHROPIC_API_KEY)")
            return False

        print("  Your API key is required to use Claude.")
        print("  Get one at: https://console.anthropic.com/")
        print()

        key = input("  Enter your API key (or press Enter to skip): ").strip()

        if not key:
            return False

        if not key.startswith("sk-ant-"):
            print(f"  {Colors.YELLOW}⚠{Colors.END} Key doesn't look like an Anthropic key")
            if not self._prompt_yes_no("  Use it anyway?"):
                return False

        # Suggest adding to shell profile
        shell = os.environ.get("SHELL", "")
        if "zsh" in shell:
            profile = "~/.zshrc"
        elif "bash" in shell:
            profile = "~/.bashrc"
        else:
            profile = "your shell profile"

        print()
        print(f"  To make this permanent, add to {profile}:")
        print(f"    export ANTHROPIC_API_KEY='{key}'")
        print()

        # Set for current session
        os.environ["ANTHROPIC_API_KEY"] = key
        self.config["api_key_set"] = True

        return True

    def _setup_journal(self, quick: bool):
        """Set up the user's journal."""
        journals_dir = self.forge_root / "journals"
        template_dir = journals_dir / ".template"

        if quick:
            journal_name = "my-journal"
        else:
            print("  Your journal tracks your learning progress.")
            print()
            default_name = "my-journal"
            journal_name = input(f"  Journal name [{default_name}]: ").strip() or default_name

        journal_path = journals_dir / journal_name

        if journal_path.exists():
            print(f"  {Colors.GREEN}✓{Colors.END} Journal '{journal_name}' already exists")
        elif template_dir.exists():
            shutil.copytree(template_dir, journal_path)
            print(f"  {Colors.GREEN}✓{Colors.END} Created journal: {journal_name}")

            # Update journal README with name
            readme_path = journal_path / "README.md"
            if readme_path.exists():
                content = readme_path.read_text()
                content = content.replace("Your Journal", f"{journal_name}")
                content = content.replace("Started: [date]", f"Started: {datetime.now().strftime('%Y-%m-%d')}")
                readme_path.write_text(content)
        else:
            print(f"  {Colors.YELLOW}○{Colors.END} Journal template not found")

        self.config["journal_name"] = journal_name

    def _choose_learning_path(self, quick: bool):
        """Help user choose a learning path."""
        if quick:
            self.config["learning_path"] = "quick-start"
            print(f"  {Colors.GREEN}✓{Colors.END} Starting with Quick Start path")
            return

        print("  Choose your learning path:")
        print()
        print("  1. Quick Start (30 min)")
        print("     → Send your first message to Claude")
        print()
        print("  2. Chatbot Developer (2-3 hours)")
        print("     → Build a conversational assistant")
        print()
        print("  3. Document Processor (2-3 hours)")
        print("     → Analyze and extract from documents")
        print()
        print("  4. Explore on my own")
        print()

        choice = input("  Your choice [1]: ").strip() or "1"

        paths = {
            "1": "quick-start",
            "2": "chatbot-developer",
            "3": "document-processor",
            "4": "explore",
        }

        self.config["learning_path"] = paths.get(choice, "quick-start")
        print(f"  {Colors.GREEN}✓{Colors.END} Selected: {self.config['learning_path']}")

    def _print_summary(self):
        """Print setup summary and next steps."""
        print()
        print(f"{Colors.BOLD}{'=' * 50}{Colors.END}")
        print(f"{Colors.BOLD}   Setup Complete!{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 50}{Colors.END}")
        print()

        # Configuration summary
        if self.config.get("api_key_set"):
            print(f"  {Colors.GREEN}✓{Colors.END} API key configured")

        if self.config.get("journal_name"):
            print(f"  {Colors.GREEN}✓{Colors.END} Journal: {self.config['journal_name']}")

        if self.config.get("learning_path"):
            print(f"  {Colors.GREEN}✓{Colors.END} Path: {self.config['learning_path']}")

        # Next steps
        print()
        print(f"{Colors.BOLD}Next Steps:{Colors.END}")
        print()

        path = self.config.get("learning_path", "quick-start")

        if path == "quick-start":
            print("  1. Read: curriculum/nodes/fundamentals/sdk-setup/README.md")
            print("  2. Run:  python curriculum/nodes/fundamentals/sdk-setup/examples/verify_installation.py")
            print("  3. Try:  python curriculum/nodes/fundamentals/first-message/examples/hello_claude.py")

        elif path == "chatbot-developer":
            print("  1. Complete the Quick Start path first")
            print("  2. Study: curriculum/nodes/messaging/multi-turn/README.md")
            print("  3. Build: blueprints/conversational-assistant/")

        elif path == "document-processor":
            print("  1. Complete the Quick Start path first")
            print("  2. Study: curriculum/nodes/messaging/vision/README.md")
            print("  3. Build: blueprints/document-processor/")

        else:
            print("  1. Explore curriculum/ for learning nodes")
            print("  2. Check blueprints/ for app patterns")
            print("  3. Use 'python .forge/cli/progress.py' to track progress")

        print()
        print("  Run 'python .forge/cli/progress.py' to track your progress")
        print()

    def _prompt_yes_no(self, prompt: str) -> bool:
        """Prompt for yes/no answer."""
        response = input(f"{prompt} (y/n): ").strip().lower()
        return response in ("y", "yes")

    def check_only(self) -> bool:
        """Just check prerequisites without full setup."""
        print(f"{Colors.BOLD}Checking Prerequisites{Colors.END}")
        print("-" * 40)
        return self._check_prerequisites()


def main():
    parser = argparse.ArgumentParser(description="Claude App Forge Setup Wizard")
    parser.add_argument("--check", action="store_true", help="Just check prerequisites")
    parser.add_argument("--quick", action="store_true", help="Quick setup with defaults")

    args = parser.parse_args()

    # Find forge root
    forge_root = Path(__file__).parent.parent.parent

    wizard = SetupWizard(forge_root)

    try:
        if args.check:
            success = wizard.check_only()
        else:
            success = wizard.run(quick=args.quick)

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)


if __name__ == "__main__":
    main()
