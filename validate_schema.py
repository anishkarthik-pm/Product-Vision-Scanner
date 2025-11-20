"""
JSON Schema Validator for Compliance Reports

Validates analyzer output against the defined JSON schema.
"""

import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError, SchemaError


def load_schema(schema_path: str = "schema.json") -> dict:
    """Load the JSON schema."""
    with open(schema_path, "r") as f:
        return json.load(f)


def load_report(report_path: str) -> dict:
    """Load a compliance report."""
    with open(report_path, "r") as f:
        return json.load(f)


def validate_report(report: dict, schema: dict) -> tuple[bool, str]:
    """
    Validate a report against the schema.

    Args:
        report: The compliance report to validate
        schema: The JSON schema

    Returns:
        Tuple of (is_valid, message)
    """
    try:
        validate(instance=report, schema=schema)
        return True, "Report is valid!"
    except ValidationError as e:
        return False, f"Validation error: {e.message}\nPath: {' -> '.join(str(p) for p in e.path)}"
    except SchemaError as e:
        return False, f"Schema error: {e.message}"


def main():
    """Main validation function."""
    if len(sys.argv) < 2:
        print("Usage: python validate_schema.py <report.json>")
        print("\nValidates a compliance report against schema.json")
        sys.exit(1)

    report_path = sys.argv[1]

    if not Path(report_path).exists():
        print(f"Error: Report file not found: {report_path}")
        sys.exit(1)

    print(f"Loading schema...")
    try:
        schema = load_schema()
        print("✓ Schema loaded")
    except Exception as e:
        print(f"✗ Error loading schema: {e}")
        sys.exit(1)

    print(f"Loading report: {report_path}")
    try:
        report = load_report(report_path)
        print("✓ Report loaded")
    except Exception as e:
        print(f"✗ Error loading report: {e}")
        sys.exit(1)

    print("Validating report...")
    is_valid, message = validate_report(report, schema)

    if is_valid:
        print(f"✓ {message}")
        print("\nReport Summary:")
        print(f"  - Report ID: {report.get('report_id')}")
        print(f"  - Products: {report.get('overall_compliance', {}).get('total_products', 0)}")
        print(f"  - Status: {report.get('overall_compliance', {}).get('status', 'unknown')}")
        print(f"  - Violations: {report.get('overall_compliance', {}).get('violation_count', 0)}")
        sys.exit(0)
    else:
        print(f"✗ {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
