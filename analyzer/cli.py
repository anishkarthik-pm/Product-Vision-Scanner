"""
Command-line interface for Retail Compliance Analyzer
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .compliance_analyzer import RetailComplianceAnalyzer


def print_summary(result: dict) -> None:
    """
    Print a human-readable summary of the analysis.

    Args:
        result: Analysis result dictionary
    """
    print("\n" + "=" * 60)
    print("RETAIL COMPLIANCE ANALYSIS REPORT")
    print("=" * 60)

    # Report metadata
    print(f"\nReport ID: {result.get('report_id', 'N/A')}")
    print(f"Timestamp: {result.get('timestamp', 'N/A')}")
    print(f"Status: {result.get('analysis_status', 'N/A')}")

    # Image info
    if "image_metadata" in result:
        meta = result["image_metadata"]
        print(f"\nImage: {meta.get('filename', 'N/A')}")
        print(f"Resolution: {meta.get('resolution', 'N/A')}")
        print(f"Quality Score: {meta.get('quality_score', 'N/A'):.2f}")

    # Overall compliance
    if "overall_compliance" in result:
        comp = result["overall_compliance"]
        print(f"\n{'=' * 60}")
        print("OVERALL COMPLIANCE")
        print("=" * 60)
        print(f"Status: {comp.get('status', 'N/A').upper()}")
        print(f"Total Products: {comp.get('total_products', 0)}")
        print(f"Compliant: {comp.get('compliant_count', 0)}")
        print(f"Violations: {comp.get('violation_count', 0)}")

        if comp.get("critical_violations"):
            print("\nCRITICAL VIOLATIONS:")
            for violation in comp["critical_violations"]:
                print(f"  - {violation}")

        if comp.get("summary"):
            print(f"\nSummary: {comp['summary']}")

    # Product details
    products = result.get("products", [])
    if products:
        print(f"\n{'=' * 60}")
        print(f"PRODUCTS ANALYZED ({len(products)})")
        print("=" * 60)

        for i, product in enumerate(products, 1):
            print(f"\n{i}. {product.get('name', 'Unknown Product')}")
            print(f"   Product ID: {product.get('product_id', 'N/A')}")

            if product.get("brand"):
                print(f"   Brand: {product['brand']}")

            if product.get("category"):
                print(f"   Category: {product['category']}")

            # Dates
            if "dates" in product:
                dates = product["dates"]
                if dates.get("expiration_date"):
                    print(f"   Expiration: {dates['expiration_date']} ({dates.get('date_visibility', 'N/A')})")

            # Condition
            if "condition" in product:
                cond = product["condition"]
                status = cond.get("status", "unknown")
                print(f"   Condition: {status.upper()}")
                if cond.get("damage_type"):
                    print(f"   Damage: {', '.join(cond['damage_type'])}")

            # Compliance
            if "compliance" in product:
                comp_prod = product["compliance"]
                is_compliant = comp_prod.get("is_compliant")
                if is_compliant is not None:
                    print(f"   Compliant: {'YES' if is_compliant else 'NO'}")

                violations = comp_prod.get("violations", [])
                if violations:
                    print("   Violations:")
                    for v in violations:
                        print(f"     - [{v.get('severity', 'unknown').upper()}] {v.get('type', 'unknown')}: {v.get('description', '')}")

            # Confidence
            confidence = product.get("confidence", 0)
            print(f"   Confidence: {confidence:.2f}")

    # Notes
    if result.get("notes"):
        print(f"\n{'=' * 60}")
        print("NOTES")
        print("=" * 60)
        print(result["notes"])

    print("\n" + "=" * 60 + "\n")


def analyze_command(args: argparse.Namespace) -> int:
    """
    Execute the analyze command.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Validate input file
    if not Path(args.image).exists():
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        return 1

    try:
        # Initialize analyzer
        analyzer = RetailComplianceAnalyzer()

        print(f"Analyzing image: {args.image}")
        print("This may take a few moments...\n")

        # Analyze image
        if args.output:
            result = analyzer.analyze_and_save(
                args.image,
                args.output,
                pretty=not args.compact
            )
            print(f"Analysis complete! Results saved to: {args.output}")
        else:
            result = analyzer.analyze_image(args.image)

        # Print summary unless quiet mode
        if not args.quiet:
            print_summary(result)

        # Print JSON if requested
        if args.json and not args.output:
            if args.compact:
                print(json.dumps(result))
            else:
                print(json.dumps(result, indent=2))

        # Exit with error code if analysis failed
        if result.get("analysis_status") == "failed":
            return 1

        return 0

    except Exception as e:
        print(f"Error during analysis: {str(e)}", file=sys.stderr)
        return 1


def main() -> int:
    """
    Main entry point for CLI.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Retail Compliance Analyzer - AI-powered store image analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze an image and display summary
  python -m analyzer.cli analyze store_photo.jpg

  # Analyze and save to JSON file
  python -m analyzer.cli analyze store_photo.jpg --output report.json

  # Analyze and output JSON to stdout
  python -m analyzer.cli analyze store_photo.jpg --json --quiet

  # Compact JSON output
  python -m analyzer.cli analyze store_photo.jpg --json --compact --quiet
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a retail store image"
    )
    analyze_parser.add_argument(
        "image",
        help="Path to the image file to analyze"
    )
    analyze_parser.add_argument(
        "-o", "--output",
        help="Save results to JSON file"
    )
    analyze_parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output results as JSON to stdout"
    )
    analyze_parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress summary output"
    )
    analyze_parser.add_argument(
        "-c", "--compact",
        action="store_true",
        help="Use compact JSON format (no indentation)"
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "analyze":
        return analyze_command(args)

    return 1


if __name__ == "__main__":
    sys.exit(main())
