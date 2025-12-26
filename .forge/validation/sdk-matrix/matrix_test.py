"""
SDK Version Matrix Testing

Tests curriculum examples against multiple SDK versions to ensure compatibility.
Generates a compatibility matrix showing which examples work with which SDK versions.

Usage:
    python matrix_test.py                    # Test current SDK
    python matrix_test.py --versions 0.39.0 0.40.0  # Test specific versions
    python matrix_test.py --all              # Test all supported versions
    python matrix_test.py --report           # Generate HTML report
"""

import argparse
import json
import subprocess
import sys
import tempfile
import venv
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# Supported SDK versions for testing
SUPPORTED_VERSIONS = [
    "0.35.0",
    "0.36.0",
    "0.37.0",
    "0.38.0",
    "0.39.0",
    "0.40.0",
]

# Minimum version requirements for specific features
FEATURE_REQUIREMENTS = {
    "streaming": "0.35.0",
    "tool_use": "0.35.0",
    "vision": "0.35.0",
    "messages_api": "0.35.0",
}


@dataclass
class TestResult:
    """Result of testing a single example."""

    example_path: str
    sdk_version: str
    passed: bool
    error: Optional[str] = None
    duration_ms: float = 0


@dataclass
class MatrixResult:
    """Complete matrix test results."""

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    python_version: str = field(default_factory=lambda: sys.version.split()[0])
    results: list[TestResult] = field(default_factory=list)

    def add_result(self, result: TestResult):
        self.results.append(result)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "python_version": self.python_version,
            "results": [
                {
                    "example": r.example_path,
                    "sdk_version": r.sdk_version,
                    "passed": r.passed,
                    "error": r.error,
                    "duration_ms": r.duration_ms,
                }
                for r in self.results
            ],
        }

    def get_summary(self) -> dict:
        """Get summary statistics."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        # Group by version
        by_version = {}
        for r in self.results:
            if r.sdk_version not in by_version:
                by_version[r.sdk_version] = {"passed": 0, "failed": 0}
            if r.passed:
                by_version[r.sdk_version]["passed"] += 1
            else:
                by_version[r.sdk_version]["failed"] += 1

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "by_version": by_version,
        }


class SDKMatrixTester:
    """Tests examples against multiple SDK versions."""

    def __init__(self, forge_root: Path):
        self.forge_root = forge_root
        self.examples_dirs = [
            forge_root / "curriculum" / "nodes",
            forge_root / "blueprints",
        ]

    def find_examples(self) -> list[Path]:
        """Find all Python examples to test."""
        examples = []
        for base_dir in self.examples_dirs:
            if base_dir.exists():
                for py_file in base_dir.rglob("examples/*.py"):
                    examples.append(py_file)
        return sorted(examples)

    def create_venv(self, sdk_version: str) -> Path:
        """Create a virtual environment with a specific SDK version."""
        venv_dir = Path(tempfile.mkdtemp(prefix=f"sdk_{sdk_version}_"))
        venv.create(venv_dir, with_pip=True)

        # Install the specific SDK version
        pip_path = venv_dir / "bin" / "pip"
        subprocess.run(
            [str(pip_path), "install", f"anthropic=={sdk_version}", "-q"],
            check=True,
            capture_output=True,
        )

        return venv_dir

    def test_example(
        self,
        example_path: Path,
        venv_dir: Path,
        sdk_version: str,
    ) -> TestResult:
        """Test a single example with a specific SDK version."""
        import time

        python_path = venv_dir / "bin" / "python"

        start = time.time()
        try:
            # Run with validation mode enabled
            env = {
                "FORGE_VALIDATION_MODE": "1",
                "PATH": str(venv_dir / "bin"),
            }

            result = subprocess.run(
                [str(python_path), str(example_path)],
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
            )

            duration_ms = (time.time() - start) * 1000

            if result.returncode == 0:
                return TestResult(
                    example_path=str(example_path.relative_to(self.forge_root)),
                    sdk_version=sdk_version,
                    passed=True,
                    duration_ms=duration_ms,
                )
            else:
                return TestResult(
                    example_path=str(example_path.relative_to(self.forge_root)),
                    sdk_version=sdk_version,
                    passed=False,
                    error=result.stderr[:500] if result.stderr else "Unknown error",
                    duration_ms=duration_ms,
                )

        except subprocess.TimeoutExpired:
            return TestResult(
                example_path=str(example_path.relative_to(self.forge_root)),
                sdk_version=sdk_version,
                passed=False,
                error="Timeout (30s)",
                duration_ms=30000,
            )
        except Exception as e:
            return TestResult(
                example_path=str(example_path.relative_to(self.forge_root)),
                sdk_version=sdk_version,
                passed=False,
                error=str(e),
                duration_ms=(time.time() - start) * 1000,
            )

    def run_matrix(self, versions: list[str]) -> MatrixResult:
        """Run the full test matrix."""
        matrix = MatrixResult()
        examples = self.find_examples()

        print(f"Found {len(examples)} examples to test")
        print(f"Testing against {len(versions)} SDK versions: {', '.join(versions)}")
        print()

        for version in versions:
            print(f"Testing SDK {version}...")
            try:
                venv_dir = self.create_venv(version)

                for example in examples:
                    result = self.test_example(example, venv_dir, version)
                    matrix.add_result(result)

                    status = "✓" if result.passed else "✗"
                    print(f"  {status} {example.name}")

                # Cleanup venv
                import shutil
                shutil.rmtree(venv_dir, ignore_errors=True)

            except Exception as e:
                print(f"  Error setting up SDK {version}: {e}")

            print()

        return matrix


def generate_html_report(matrix: MatrixResult, output_path: Path):
    """Generate an HTML report of the test results."""
    summary = matrix.get_summary()

    # Build example rows
    examples = set(r.example_path for r in matrix.results)
    versions = sorted(set(r.sdk_version for r in matrix.results))

    # Create lookup
    lookup = {(r.example_path, r.sdk_version): r for r in matrix.results}

    rows = []
    for example in sorted(examples):
        cells = [f"<td>{example}</td>"]
        for version in versions:
            result = lookup.get((example, version))
            if result:
                if result.passed:
                    cells.append('<td class="pass">✓</td>')
                else:
                    cells.append(f'<td class="fail" title="{result.error}">✗</td>')
            else:
                cells.append('<td class="na">-</td>')
        rows.append(f"<tr>{''.join(cells)}</tr>")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>SDK Compatibility Matrix</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; margin: 2rem; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background: #333; color: white; }}
        .pass {{ background: #d4edda; color: #155724; }}
        .fail {{ background: #f8d7da; color: #721c24; cursor: help; }}
        .na {{ background: #e9ecef; color: #6c757d; }}
        .example {{ text-align: left; font-family: monospace; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>SDK Compatibility Matrix</h1>

    <div class="summary">
        <p><strong>Generated:</strong> {matrix.timestamp}</p>
        <p><strong>Python Version:</strong> {matrix.python_version}</p>
        <p><strong>Results:</strong> {summary['passed']}/{summary['total']} passed ({summary['pass_rate']:.1f}%)</p>
    </div>

    <table>
        <thead>
            <tr>
                <th>Example</th>
                {''.join(f'<th>{v}</th>' for v in versions)}
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>

    <p style="margin-top: 2rem; color: #666;">
        ✓ = Passed, ✗ = Failed (hover for error), - = Not tested
    </p>
</body>
</html>"""

    output_path.write_text(html)
    print(f"Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="SDK Version Matrix Testing")
    parser.add_argument(
        "--versions",
        nargs="+",
        default=None,
        help="Specific SDK versions to test",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all supported versions",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate HTML report",
    )
    parser.add_argument(
        "--output",
        default="sdk_matrix_report.html",
        help="Output file for report",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    # Determine versions to test
    if args.versions:
        versions = args.versions
    elif args.all:
        versions = SUPPORTED_VERSIONS
    else:
        # Default: test current installed version
        try:
            import anthropic
            versions = [anthropic.__version__]
        except ImportError:
            print("Anthropic SDK not installed. Use --versions to specify.")
            sys.exit(1)

    # Find forge root
    forge_root = Path(__file__).parent.parent.parent

    # Run tests
    tester = SDKMatrixTester(forge_root)
    matrix = tester.run_matrix(versions)

    # Output results
    summary = matrix.get_summary()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Pass Rate: {summary['pass_rate']:.1f}%")

    if args.json:
        print()
        print(json.dumps(matrix.to_dict(), indent=2))

    if args.report:
        generate_html_report(matrix, Path(args.output))

    # Exit with failure if any tests failed
    sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
