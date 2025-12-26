#!/usr/bin/env python3
"""
Blueprint Validation Runner

Validates that a blueprint implementation meets all criteria.
Can be run manually or as part of CI/CD.

Usage:
    python validate_blueprint.py conversational-assistant ./my-assistant
    python validate_blueprint.py document-processor ./my-processor --strict
"""

import argparse
import importlib.util
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class ValidationResult:
    """Result of a single validation check."""

    name: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info


class BlueprintValidator:
    """Validates blueprint implementations."""

    def __init__(self, blueprint_id: str, implementation_path: str, strict: bool = False):
        self.blueprint_id = blueprint_id
        self.impl_path = Path(implementation_path)
        self.strict = strict
        self.results: list[ValidationResult] = []

        # Load blueprint specification
        self.spec = self._load_specification()

    def _load_specification(self) -> dict:
        """Load the blueprint specification."""
        blueprints_dir = Path(__file__).parent.parent
        spec_path = blueprints_dir / self.blueprint_id / "specification.yaml"

        if not spec_path.exists():
            # Try decisions.yaml as fallback
            spec_path = blueprints_dir / self.blueprint_id / "decisions.yaml"

        if spec_path.exists():
            with open(spec_path) as f:
                return yaml.safe_load(f)
        return {}

    def validate(self) -> bool:
        """Run all validation checks."""
        self._check_directory_exists()
        self._check_required_files()
        self._check_python_syntax()
        self._check_imports()
        self._check_core_components()
        self._check_configuration()
        self._check_tests_exist()

        return self._summarize()

    def _add_result(self, name: str, passed: bool, message: str, severity: str = "error"):
        """Add a validation result."""
        self.results.append(ValidationResult(
            name=name,
            passed=passed,
            message=message,
            severity=severity,
        ))

    def _check_directory_exists(self):
        """Check if the implementation directory exists."""
        if self.impl_path.exists() and self.impl_path.is_dir():
            self._add_result(
                "directory_exists",
                True,
                f"Implementation directory exists: {self.impl_path}",
            )
        else:
            self._add_result(
                "directory_exists",
                False,
                f"Implementation directory not found: {self.impl_path}",
            )

    def _check_required_files(self):
        """Check for required files based on blueprint."""
        required_files = {
            "conversational-assistant": [
                "main.py",
                "assistant.py",
                "conversation.py",
                "config.py",
            ],
            "document-processor": [
                "main.py",
                "processor.py",
                "tools.py",
                "config.py",
            ],
        }

        files = required_files.get(self.blueprint_id, ["main.py"])

        for filename in files:
            # Check in root and src/
            found = (
                (self.impl_path / filename).exists()
                or (self.impl_path / "src" / filename).exists()
            )
            self._add_result(
                f"file_{filename}",
                found,
                f"Required file '{filename}': {'found' if found else 'missing'}",
                severity="error" if not found else "info",
            )

    def _check_python_syntax(self):
        """Check Python syntax of all .py files."""
        py_files = list(self.impl_path.rglob("*.py"))

        for py_file in py_files:
            try:
                with open(py_file) as f:
                    compile(f.read(), py_file, "exec")
                self._add_result(
                    f"syntax_{py_file.name}",
                    True,
                    f"Syntax OK: {py_file.name}",
                    severity="info",
                )
            except SyntaxError as e:
                self._add_result(
                    f"syntax_{py_file.name}",
                    False,
                    f"Syntax error in {py_file.name}: {e}",
                )

    def _check_imports(self):
        """Check that required imports are present."""
        main_file = self.impl_path / "main.py"
        if not main_file.exists():
            main_file = self.impl_path / "src" / "main.py"

        if main_file.exists():
            content = main_file.read_text()

            # Check for anthropic import
            if "anthropic" in content or "from anthropic" in content:
                self._add_result(
                    "import_anthropic",
                    True,
                    "Anthropic SDK import found",
                    severity="info",
                )
            else:
                self._add_result(
                    "import_anthropic",
                    False,
                    "Anthropic SDK import not found in main.py",
                    severity="warning",
                )

    def _check_core_components(self):
        """Check for core component implementations."""
        if self.blueprint_id == "conversational-assistant":
            self._check_assistant_components()
        elif self.blueprint_id == "document-processor":
            self._check_processor_components()

    def _check_assistant_components(self):
        """Check conversational assistant specific components."""
        # Check for conversation history management
        all_content = self._read_all_python_files()

        checks = [
            ("history" in all_content.lower() or "messages" in all_content.lower(),
             "conversation_history", "Conversation history management"),
            ("stream" in all_content.lower(),
             "streaming", "Streaming support"),
            ("system" in all_content.lower() and "prompt" in all_content.lower(),
             "system_prompt", "System prompt handling"),
        ]

        for found, name, description in checks:
            self._add_result(
                f"component_{name}",
                found,
                f"{description}: {'found' if found else 'not found'}",
                severity="warning" if not found else "info",
            )

    def _check_processor_components(self):
        """Check document processor specific components."""
        all_content = self._read_all_python_files()

        checks = [
            ("tool" in all_content.lower(),
             "tools", "Tool definitions"),
            ("extract" in all_content.lower() or "process" in all_content.lower(),
             "extraction", "Extraction logic"),
        ]

        for found, name, description in checks:
            self._add_result(
                f"component_{name}",
                found,
                f"{description}: {'found' if found else 'not found'}",
                severity="warning" if not found else "info",
            )

    def _check_configuration(self):
        """Check for configuration handling."""
        config_file = self.impl_path / "config.py"
        if not config_file.exists():
            config_file = self.impl_path / "src" / "config.py"

        if config_file.exists():
            content = config_file.read_text()
            has_env = "environ" in content or "os.getenv" in content
            self._add_result(
                "config_env",
                has_env,
                f"Environment variable support: {'yes' if has_env else 'no'}",
                severity="warning" if not has_env else "info",
            )
        else:
            self._add_result(
                "config_file",
                False,
                "Configuration file not found",
                severity="warning",
            )

    def _check_tests_exist(self):
        """Check for test files."""
        test_dirs = [
            self.impl_path / "tests",
            self.impl_path / "test",
        ]

        has_tests = any(d.exists() and list(d.glob("test_*.py")) for d in test_dirs)

        self._add_result(
            "tests_exist",
            has_tests,
            f"Test files: {'found' if has_tests else 'not found'}",
            severity="warning" if not has_tests else "info",
        )

    def _read_all_python_files(self) -> str:
        """Read all Python files into a single string."""
        content = []
        for py_file in self.impl_path.rglob("*.py"):
            try:
                content.append(py_file.read_text())
            except Exception:
                pass
        return "\n".join(content)

    def _summarize(self) -> bool:
        """Summarize validation results."""
        errors = [r for r in self.results if not r.passed and r.severity == "error"]
        warnings = [r for r in self.results if not r.passed and r.severity == "warning"]
        passed = [r for r in self.results if r.passed]

        print()
        print("=" * 60)
        print("BLUEPRINT VALIDATION REPORT")
        print("=" * 60)
        print(f"Blueprint: {self.blueprint_id}")
        print(f"Implementation: {self.impl_path}")
        print()

        if passed:
            print("✓ PASSED")
            for r in passed:
                print(f"  ✓ {r.name}: {r.message}")

        if warnings:
            print()
            print("⚠ WARNINGS")
            for r in warnings:
                print(f"  ⚠ {r.name}: {r.message}")

        if errors:
            print()
            print("✗ ERRORS")
            for r in errors:
                print(f"  ✗ {r.name}: {r.message}")

        print()
        print("-" * 60)
        print(f"Results: {len(passed)} passed, {len(warnings)} warnings, {len(errors)} errors")

        if errors:
            print("Status: FAILED")
            return False
        elif warnings and self.strict:
            print("Status: FAILED (strict mode)")
            return False
        else:
            print("Status: PASSED")
            return True


def main():
    parser = argparse.ArgumentParser(description="Validate blueprint implementation")
    parser.add_argument("blueprint", help="Blueprint ID (e.g., conversational-assistant)")
    parser.add_argument("path", help="Path to implementation")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    args = parser.parse_args()

    validator = BlueprintValidator(
        blueprint_id=args.blueprint,
        implementation_path=args.path,
        strict=args.strict,
    )

    success = validator.validate()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
