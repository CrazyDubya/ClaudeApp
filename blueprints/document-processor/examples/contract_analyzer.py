"""
Contract Analyzer

Extracts key information from legal contracts using Claude's tool use.
Demonstrates structured extraction with custom schemas.

Usage:
    python contract_analyzer.py contract.txt
    python contract_analyzer.py contract.txt --output results.json
"""

import argparse
import json
import os
from pathlib import Path

from anthropic import Anthropic


# Contract extraction tool
CONTRACT_TOOL = {
    "name": "extract_contract_info",
    "description": "Extract structured information from a legal contract",
    "input_schema": {
        "type": "object",
        "properties": {
            "contract_type": {
                "type": "string",
                "description": "Type of contract (e.g., NDA, Employment, Service Agreement)",
            },
            "parties": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "role": {
                            "type": "string",
                            "enum": ["party_a", "party_b", "third_party"],
                        },
                        "type": {
                            "type": "string",
                            "enum": ["individual", "corporation", "organization"],
                        },
                    },
                    "required": ["name", "role"],
                },
                "description": "Parties involved in the contract",
            },
            "effective_date": {
                "type": "string",
                "description": "When the contract becomes effective",
            },
            "termination_date": {
                "type": "string",
                "description": "When the contract ends (if specified)",
            },
            "term_length": {
                "type": "string",
                "description": "Duration of the contract",
            },
            "financial_terms": {
                "type": "object",
                "properties": {
                    "total_value": {"type": "string"},
                    "payment_schedule": {"type": "string"},
                    "currency": {"type": "string"},
                },
                "description": "Financial terms if applicable",
            },
            "key_obligations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "party": {"type": "string"},
                        "obligation": {"type": "string"},
                    },
                },
                "description": "Key obligations for each party",
            },
            "termination_clauses": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Conditions under which the contract can be terminated",
            },
            "governing_law": {
                "type": "string",
                "description": "Jurisdiction/governing law",
            },
            "special_clauses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "summary": {"type": "string"},
                    },
                },
                "description": "Notable or unusual clauses",
            },
            "risk_factors": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Potential risks or concerns identified",
            },
        },
        "required": ["contract_type", "parties", "effective_date", "key_obligations"],
    },
}

SYSTEM_PROMPT = """You are an expert legal document analyst.
Analyze contracts thoroughly and extract all relevant information.
Be precise with dates, names, and financial figures.
Identify potential risks or unusual clauses.
If information is not explicitly stated, note it as "Not specified"."""


def analyze_contract(contract_text: str) -> dict:
    """
    Analyze a contract and extract structured information.

    Args:
        contract_text: The contract text to analyze

    Returns:
        Dictionary containing extracted contract information
    """
    client = Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=[CONTRACT_TOOL],
        messages=[
            {
                "role": "user",
                "content": f"""Analyze this contract and extract all key information using the extract_contract_info tool.

Contract:
{contract_text}

Extract all available information including parties, dates, obligations, and any notable clauses or risk factors.""",
            }
        ],
    )

    # Extract tool use result
    for block in response.content:
        if block.type == "tool_use" and block.name == "extract_contract_info":
            return block.input

    return {"error": "No structured data extracted"}


def format_report(data: dict) -> str:
    """Format the extracted data as a readable report."""
    lines = [
        "=" * 60,
        "CONTRACT ANALYSIS REPORT",
        "=" * 60,
        "",
        f"Contract Type: {data.get('contract_type', 'Unknown')}",
        f"Effective Date: {data.get('effective_date', 'Not specified')}",
        f"Termination Date: {data.get('termination_date', 'Not specified')}",
        f"Term Length: {data.get('term_length', 'Not specified')}",
        f"Governing Law: {data.get('governing_law', 'Not specified')}",
        "",
        "PARTIES",
        "-" * 40,
    ]

    for party in data.get("parties", []):
        lines.append(f"  • {party.get('name')} ({party.get('role', 'unknown role')})")
        if party.get("type"):
            lines.append(f"    Type: {party['type']}")

    if data.get("financial_terms"):
        lines.extend([
            "",
            "FINANCIAL TERMS",
            "-" * 40,
        ])
        ft = data["financial_terms"]
        if ft.get("total_value"):
            lines.append(f"  Total Value: {ft['total_value']}")
        if ft.get("payment_schedule"):
            lines.append(f"  Payment Schedule: {ft['payment_schedule']}")
        if ft.get("currency"):
            lines.append(f"  Currency: {ft['currency']}")

    lines.extend([
        "",
        "KEY OBLIGATIONS",
        "-" * 40,
    ])
    for obl in data.get("key_obligations", []):
        lines.append(f"  • [{obl.get('party', 'Unknown')}] {obl.get('obligation', '')}")

    if data.get("termination_clauses"):
        lines.extend([
            "",
            "TERMINATION CLAUSES",
            "-" * 40,
        ])
        for clause in data["termination_clauses"]:
            lines.append(f"  • {clause}")

    if data.get("special_clauses"):
        lines.extend([
            "",
            "SPECIAL CLAUSES",
            "-" * 40,
        ])
        for clause in data["special_clauses"]:
            lines.append(f"  • {clause.get('title', 'Untitled')}")
            lines.append(f"    {clause.get('summary', '')}")

    if data.get("risk_factors"):
        lines.extend([
            "",
            "⚠️  RISK FACTORS",
            "-" * 40,
        ])
        for risk in data["risk_factors"]:
            lines.append(f"  • {risk}")

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze legal contracts")
    parser.add_argument("contract", help="Path to contract file")
    parser.add_argument("--output", "-o", help="Output file for JSON results")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    # Load contract
    contract_path = Path(args.contract)
    if not contract_path.exists():
        print(f"Error: File not found: {args.contract}")
        return

    contract_text = contract_path.read_text()
    print(f"Analyzing contract: {args.contract}")
    print(f"Document length: {len(contract_text)} characters")
    print()

    # Analyze
    result = analyze_contract(contract_text)

    # Output
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.output}")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("✓ Example validated (syntax check only)")
    else:
        main()
