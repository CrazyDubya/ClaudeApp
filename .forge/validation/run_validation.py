#!/usr/bin/env python3
"""
Validation Runner for Claude App Forge

Runs validation tests against curriculum examples and exercises
to ensure they work with the current Claude SDK version.

Usage:
    python run_validation.py              # Run all tests
    python run_validation.py --unit       # Run only unit tests (no API)
    python run_validation.py --live       # Run only live API tests
    python run_validation.py --report     # Generate HTML report
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []

    try:
        import pytest
    except ImportError:
        missing.append("pytest")

    try:
        import anthropic
    except ImportError:
        missing.append("anthropic")

    if missing:
        print("Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with: pip install " + " ".join(missing))
        return False

    return True


def run_tests(args):
    """Run the validation tests."""
    # Build pytest command
    cmd = ["pytest"]

    # Add test directory
    test_dir = Path(__file__).parent / "tests"
    cmd.append(str(test_dir))

    # Add verbosity
    if args.verbose:
        cmd.append("-v")

    # Add markers
    if args.unit:
        cmd.extend(["-m", "not live"])
    elif args.live:
        cmd.extend(["-m", "live"])

    # Add report
    if args.report:
        report_file = f"validation_report_{datetime.now():%Y%m%d_%H%M%S}.html"
        cmd.extend(["--html", report_file])

    # Run tests
    print(f"Running: {' '.join(cmd)}")
    print("=" * 50)

    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def check_sdk_version():
    """Display SDK version information."""
    try:
        import anthropic

        print(f"Anthropic SDK version: {anthropic.__version__}")
    except ImportError:
        print("Anthropic SDK not installed")


def check_api_key():
    """Check API key configuration."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        masked = f"{key[:7]}...{key[-4:]}" if len(key) > 15 else "***"
        print(f"API key configured: {masked}")
        return True
    else:
        print("API key not configured (live tests will be skipped)")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run validation tests for Claude App Forge"
    )
    parser.add_argument(
        "--unit", action="store_true", help="Run only unit tests (no API required)"
    )
    parser.add_argument(
        "--live", action="store_true", help="Run only live API tests"
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate HTML report"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--check", action="store_true", help="Check environment only"
    )

    args = parser.parse_args()

    print("Claude App Forge - Validation Runner")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Show environment info
    check_sdk_version()
    check_api_key()
    print()

    if args.check:
        print("Environment check complete.")
        sys.exit(0)

    # Run tests
    exit_code = run_tests(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
