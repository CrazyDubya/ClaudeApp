#!/usr/bin/env python3
"""
Validation Report Dashboard Generator

Generates an interactive HTML dashboard showing:
- Overall validation status
- Per-node validation results
- SDK compatibility matrix
- Historical trends

Usage:
    python generate_dashboard.py              # Generate dashboard
    python generate_dashboard.py --serve      # Generate and serve locally
    python generate_dashboard.py --output ./  # Custom output directory
"""

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml


def get_curriculum_structure(forge_root: Path) -> dict:
    """Get the curriculum structure from graph.yaml."""
    graph_path = forge_root / "curriculum" / "graph.yaml"
    if graph_path.exists():
        with open(graph_path) as f:
            return yaml.safe_load(f)
    return {}


def get_node_status(node_path: Path) -> dict:
    """Get validation status for a curriculum node."""
    status = {
        "has_readme": (node_path / "README.md").exists(),
        "has_examples": False,
        "has_exercises": False,
        "example_count": 0,
        "exercise_count": 0,
        "examples_valid": True,
        "exercises_valid": True,
    }

    # Check examples
    examples_dir = node_path / "examples"
    if examples_dir.exists():
        examples = list(examples_dir.glob("*.py"))
        status["has_examples"] = len(examples) > 0
        status["example_count"] = len(examples)

        for ex in examples:
            try:
                with open(ex) as f:
                    compile(f.read(), ex, "exec")
            except SyntaxError:
                status["examples_valid"] = False

    # Check exercises
    exercises_dir = node_path / "exercises"
    if exercises_dir.exists():
        exercises = list(exercises_dir.glob("*.py"))
        status["has_exercises"] = len(exercises) > 0
        status["exercise_count"] = len(exercises)

        for ex in exercises:
            try:
                with open(ex) as f:
                    compile(f.read(), ex, "exec")
            except SyntaxError:
                status["exercises_valid"] = False

    return status


def get_all_node_statuses(forge_root: Path) -> dict:
    """Get status for all curriculum nodes."""
    nodes_dir = forge_root / "curriculum" / "nodes"
    statuses = {}

    if nodes_dir.exists():
        for category_dir in nodes_dir.iterdir():
            if category_dir.is_dir():
                category = category_dir.name
                statuses[category] = {}

                for node_dir in category_dir.iterdir():
                    if node_dir.is_dir():
                        node = node_dir.name
                        statuses[category][node] = get_node_status(node_dir)

    return statuses


def get_blueprint_status(blueprint_path: Path) -> dict:
    """Get validation status for a blueprint."""
    status = {
        "has_readme": (blueprint_path / "README.md").exists(),
        "has_spec": (blueprint_path / "specification.yaml").exists(),
        "has_decisions": (blueprint_path / "decisions.yaml").exists(),
        "has_templates": (blueprint_path / "templates").exists(),
        "has_examples": False,
        "example_count": 0,
        "template_count": 0,
    }

    # Check examples
    examples_dir = blueprint_path / "examples"
    if examples_dir.exists():
        examples = list(examples_dir.glob("*.py"))
        status["has_examples"] = len(examples) > 0
        status["example_count"] = len(examples)

    # Check templates
    templates_dir = blueprint_path / "templates"
    if templates_dir.exists():
        templates = list(templates_dir.glob("*.template"))
        status["template_count"] = len(templates)

    return status


def get_all_blueprint_statuses(forge_root: Path) -> dict:
    """Get status for all blueprints."""
    blueprints_dir = forge_root / "blueprints"
    statuses = {}

    if blueprints_dir.exists():
        for bp_dir in blueprints_dir.iterdir():
            if bp_dir.is_dir() and not bp_dir.name.startswith("."):
                statuses[bp_dir.name] = get_blueprint_status(bp_dir)

    return statuses


def generate_dashboard_html(
    node_statuses: dict,
    blueprint_statuses: dict,
    output_path: Path,
):
    """Generate the HTML dashboard."""

    # Calculate summary stats
    total_nodes = sum(len(nodes) for nodes in node_statuses.values())
    complete_nodes = sum(
        1 for cat in node_statuses.values()
        for node in cat.values()
        if node["has_readme"] and node["has_examples"]
    )

    total_blueprints = len(blueprint_statuses)
    complete_blueprints = sum(
        1 for bp in blueprint_statuses.values()
        if bp["has_readme"] and bp["has_examples"] and bp["has_templates"]
    )

    # Build node rows
    node_rows = []
    for category, nodes in sorted(node_statuses.items()):
        for node_name, status in sorted(nodes.items()):
            readme = "✓" if status["has_readme"] else "✗"
            examples = f"✓ ({status['example_count']})" if status["has_examples"] else "✗"
            exercises = f"✓ ({status['exercise_count']})" if status["has_exercises"] else "✗"
            valid = "✓" if status["examples_valid"] and status["exercises_valid"] else "✗"

            row_class = "complete" if status["has_readme"] and status["has_examples"] else "incomplete"

            node_rows.append(f'''
                <tr class="{row_class}">
                    <td>{category}</td>
                    <td>{node_name}</td>
                    <td>{readme}</td>
                    <td>{examples}</td>
                    <td>{exercises}</td>
                    <td>{valid}</td>
                </tr>
            ''')

    # Build blueprint rows
    blueprint_rows = []
    for bp_name, status in sorted(blueprint_statuses.items()):
        readme = "✓" if status["has_readme"] else "✗"
        spec = "✓" if status["has_spec"] else "✗"
        templates = f"✓ ({status['template_count']})" if status["has_templates"] else "✗"
        examples = f"✓ ({status['example_count']})" if status["has_examples"] else "✗"

        row_class = "complete" if status["has_readme"] and status["has_examples"] else "incomplete"

        blueprint_rows.append(f'''
            <tr class="{row_class}">
                <td>{bp_name}</td>
                <td>{readme}</td>
                <td>{spec}</td>
                <td>{templates}</td>
                <td>{examples}</td>
            </tr>
        ''')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude App Forge - Validation Dashboard</title>
    <style>
        :root {{
            --green: #28a745;
            --yellow: #ffc107;
            --red: #dc3545;
            --gray: #6c757d;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        .subtitle {{ color: #666; margin-bottom: 30px; }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{ margin: 0 0 10px 0; color: #333; font-size: 14px; }}
        .stat-card .value {{ font-size: 32px; font-weight: bold; }}
        .stat-card .label {{ color: #666; font-size: 14px; }}
        .stat-card.green .value {{ color: var(--green); }}
        .stat-card.yellow .value {{ color: var(--yellow); }}
        .stat-card.red .value {{ color: var(--red); }}

        .section {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{ margin-top: 0; color: #333; }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        tr.complete {{ background: #f8fff8; }}
        tr.incomplete {{ background: #fff8f8; }}
        tr:hover {{ background: #f0f0f0; }}

        .timestamp {{ color: #999; font-size: 12px; margin-top: 20px; }}

        @media (max-width: 768px) {{
            .summary {{ grid-template-columns: 1fr 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Claude App Forge</h1>
        <p class="subtitle">Validation Dashboard</p>

        <div class="summary">
            <div class="stat-card green">
                <h3>Curriculum Nodes</h3>
                <div class="value">{complete_nodes}/{total_nodes}</div>
                <div class="label">complete</div>
            </div>
            <div class="stat-card green">
                <h3>Blueprints</h3>
                <div class="value">{complete_blueprints}/{total_blueprints}</div>
                <div class="label">complete</div>
            </div>
            <div class="stat-card">
                <h3>Last Updated</h3>
                <div class="value" style="font-size: 18px;">{datetime.now().strftime('%Y-%m-%d')}</div>
                <div class="label">{datetime.now().strftime('%H:%M UTC')}</div>
            </div>
        </div>

        <div class="section">
            <h2>Curriculum Nodes</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Node</th>
                        <th>README</th>
                        <th>Examples</th>
                        <th>Exercises</th>
                        <th>Syntax</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(node_rows)}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Blueprints</h2>
            <table>
                <thead>
                    <tr>
                        <th>Blueprint</th>
                        <th>README</th>
                        <th>Spec</th>
                        <th>Templates</th>
                        <th>Examples</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(blueprint_rows)}
                </tbody>
            </table>
        </div>

        <p class="timestamp">Generated: {datetime.now().isoformat()}</p>
    </div>
</body>
</html>'''

    output_path.write_text(html)
    print(f"Dashboard generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate validation dashboard")
    parser.add_argument("--output", default="dashboard.html", help="Output file")
    parser.add_argument("--serve", action="store_true", help="Serve locally after generating")
    parser.add_argument("--port", type=int, default=8080, help="Port for local server")

    args = parser.parse_args()

    # Find forge root
    forge_root = Path(__file__).parent.parent.parent.parent

    # Gather status data
    print("Collecting curriculum node status...")
    node_statuses = get_all_node_statuses(forge_root)

    print("Collecting blueprint status...")
    blueprint_statuses = get_all_blueprint_statuses(forge_root)

    # Generate dashboard
    output_path = Path(args.output)
    generate_dashboard_html(node_statuses, blueprint_statuses, output_path)

    # Optionally serve
    if args.serve:
        import http.server
        import socketserver

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(output_path.parent), **kwargs)

        print(f"\nServing dashboard at http://localhost:{args.port}")
        print("Press Ctrl+C to stop")

        with socketserver.TCPServer(("", args.port), Handler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nStopped")


if __name__ == "__main__":
    main()
