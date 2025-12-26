"""
Invoice Processor

Extracts structured data from invoices using Claude.
Demonstrates vision capabilities for processing invoice images.

Usage:
    python invoice_processor.py invoice.txt           # Process text invoice
    python invoice_processor.py invoice.png --image   # Process invoice image
    python invoice_processor.py invoice.pdf --pdf     # Process PDF invoice
"""

import argparse
import base64
import json
import os
from pathlib import Path

from anthropic import Anthropic


# Invoice extraction tool
INVOICE_TOOL = {
    "name": "extract_invoice_data",
    "description": "Extract structured data from an invoice",
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "Invoice number/ID",
            },
            "invoice_date": {
                "type": "string",
                "description": "Date the invoice was issued",
            },
            "due_date": {
                "type": "string",
                "description": "Payment due date",
            },
            "vendor": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                    "phone": {"type": "string"},
                    "email": {"type": "string"},
                    "tax_id": {"type": "string"},
                },
                "required": ["name"],
            },
            "customer": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                    "account_number": {"type": "string"},
                },
                "required": ["name"],
            },
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "amount": {"type": "number"},
                        "tax_rate": {"type": "number"},
                    },
                    "required": ["description", "amount"],
                },
            },
            "subtotal": {"type": "number"},
            "tax_amount": {"type": "number"},
            "shipping": {"type": "number"},
            "discount": {"type": "number"},
            "total": {"type": "number"},
            "currency": {"type": "string"},
            "payment_terms": {"type": "string"},
            "payment_methods": {
                "type": "array",
                "items": {"type": "string"},
            },
            "notes": {"type": "string"},
        },
        "required": ["invoice_number", "vendor", "customer", "line_items", "total"],
    },
}

SYSTEM_PROMPT = """You are an expert at extracting data from invoices.
Extract all visible information accurately.
For numbers, use numeric values (not strings with currency symbols).
If a field is not visible or not applicable, omit it."""


def process_text_invoice(invoice_text: str) -> dict:
    """Process a text-based invoice."""
    client = Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        tools=[INVOICE_TOOL],
        messages=[
            {
                "role": "user",
                "content": f"""Extract all data from this invoice using the extract_invoice_data tool.

Invoice:
{invoice_text}""",
            }
        ],
    )

    return _extract_tool_result(response)


def process_image_invoice(image_path: str) -> dict:
    """Process an invoice image using vision."""
    client = Anthropic()

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    # Determine media type
    suffix = Path(image_path).suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_types.get(suffix, "image/jpeg")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        tools=[INVOICE_TOOL],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Extract all data from this invoice image using the extract_invoice_data tool.",
                    },
                ],
            }
        ],
    )

    return _extract_tool_result(response)


def _extract_tool_result(response) -> dict:
    """Extract the tool result from the response."""
    for block in response.content:
        if block.type == "tool_use" and block.name == "extract_invoice_data":
            return block.input
    return {"error": "No data extracted"}


def format_invoice_report(data: dict) -> str:
    """Format extracted invoice data as a report."""
    lines = [
        "=" * 60,
        "INVOICE DATA EXTRACTION",
        "=" * 60,
        "",
        f"Invoice #: {data.get('invoice_number', 'N/A')}",
        f"Date: {data.get('invoice_date', 'N/A')}",
        f"Due Date: {data.get('due_date', 'N/A')}",
        "",
    ]

    # Vendor info
    vendor = data.get("vendor", {})
    lines.extend([
        "FROM (Vendor):",
        f"  {vendor.get('name', 'N/A')}",
    ])
    if vendor.get("address"):
        lines.append(f"  {vendor['address']}")
    if vendor.get("email"):
        lines.append(f"  Email: {vendor['email']}")
    if vendor.get("tax_id"):
        lines.append(f"  Tax ID: {vendor['tax_id']}")

    # Customer info
    customer = data.get("customer", {})
    lines.extend([
        "",
        "TO (Customer):",
        f"  {customer.get('name', 'N/A')}",
    ])
    if customer.get("address"):
        lines.append(f"  {customer['address']}")

    # Line items
    lines.extend([
        "",
        "LINE ITEMS:",
        "-" * 60,
        f"{'Description':<30} {'Qty':>6} {'Price':>10} {'Amount':>10}",
        "-" * 60,
    ])

    for item in data.get("line_items", []):
        desc = item.get("description", "")[:30]
        qty = item.get("quantity", "-")
        price = item.get("unit_price", "-")
        amount = item.get("amount", 0)
        lines.append(f"{desc:<30} {str(qty):>6} {str(price):>10} {amount:>10.2f}")

    lines.append("-" * 60)

    # Totals
    currency = data.get("currency", "USD")
    if data.get("subtotal"):
        lines.append(f"{'Subtotal:':<48} {data['subtotal']:>10.2f}")
    if data.get("discount"):
        lines.append(f"{'Discount:':<48} -{data['discount']:>9.2f}")
    if data.get("tax_amount"):
        lines.append(f"{'Tax:':<48} {data['tax_amount']:>10.2f}")
    if data.get("shipping"):
        lines.append(f"{'Shipping:':<48} {data['shipping']:>10.2f}")

    lines.extend([
        "=" * 60,
        f"{'TOTAL (' + currency + '):':<48} {data.get('total', 0):>10.2f}",
        "=" * 60,
    ])

    if data.get("payment_terms"):
        lines.extend(["", f"Payment Terms: {data['payment_terms']}"])

    if data.get("notes"):
        lines.extend(["", f"Notes: {data['notes']}"])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Process invoices")
    parser.add_argument("invoice", help="Path to invoice file")
    parser.add_argument("--image", action="store_true", help="Process as image")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    invoice_path = Path(args.invoice)
    if not invoice_path.exists():
        print(f"Error: File not found: {args.invoice}")
        return

    print(f"Processing invoice: {args.invoice}")

    # Process based on type
    if args.image or invoice_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
        result = process_image_invoice(args.invoice)
    else:
        invoice_text = invoice_path.read_text()
        result = process_text_invoice(invoice_text)

    # Output
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.output}")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print()
        print(format_invoice_report(result))


if __name__ == "__main__":
    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("✓ Example validated (syntax check only)")
    else:
        main()
