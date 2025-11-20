"""
Multi-Type CLI for Retail Compliance Analyzer

Supports waste, shelf, promo, and FIFO analysis types.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .multi_type_analyzer import MultiTypeComplianceAnalyzer


def print_waste_summary(result: dict) -> None:
    """Print summary for waste analysis."""
    print("\n" + "=" * 60)
    print("WASTE/DISPOSAL ANALYSIS")
    print("=" * 60)

    print(f"\nWaste Reason: {result.get('waste_reason', 'N/A')}")
    print(f"Total Items: {result.get('estimated_total_items', 0)}")
    print(f"Image Quality: {result.get('image_quality', 'N/A')}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")

    products = result.get("products", [])
    if products:
        print(f"\n{'=' * 60}")
        print(f"PRODUCTS ({len(products)})")
        print("=" * 60)

        for i, product in enumerate(products, 1):
            print(f"\n{i}. {product.get('product_name', 'Unknown')}")
            if product.get("brand"):
                print(f"   Brand: {product['brand']}")
            print(f"   Quantity: {product.get('quantity')} {product.get('unit', '')}")
            print(f"   Condition: {product.get('condition', 'unknown').upper()}")
            print(f"   Details: {product.get('damage_details', 'N/A')}")
            if product.get("expiry_date"):
                print(f"   Expiry: {product['expiry_date']}")

    if result.get("notes"):
        print(f"\nNotes: {result['notes']}")

    print("\n" + "=" * 60 + "\n")


def print_shelf_summary(result: dict) -> None:
    """Print summary for shelf analysis."""
    print("\n" + "=" * 60)
    print("SHELF COMPLIANCE ANALYSIS")
    print("=" * 60)

    overview = result.get("shelf_overview", {})
    print(f"\nTotal Facings: {overview.get('total_facings', 0)}")
    print(f"Stocked: {overview.get('stocked_facings', 0)}")
    print(f"Empty: {overview.get('empty_facings', 0)}")
    print(f"OSA%: {overview.get('osa_percentage', 0):.1f}%")

    print(f"\nCompliance Status: {result.get('compliance_status', 'unknown').upper()}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")

    issues = result.get("issues", [])
    if issues:
        print(f"\n{'=' * 60}")
        print(f"ISSUES FOUND ({len(issues)})")
        print("=" * 60)

        for issue in issues:
            severity = issue.get('severity', 'unknown').upper()
            issue_type = issue.get('issue_type', 'unknown')
            print(f"\n[{severity}] {issue_type}")
            if issue.get('product_name'):
                print(f"Product: {issue['product_name']}")
            print(f"Description: {issue.get('description', 'N/A')}")

    print("\n" + "=" * 60 + "\n")


def print_promo_summary(result: dict) -> None:
    """Print summary for promo analysis."""
    print("\n" + "=" * 60)
    print("PROMOTIONAL COMPLIANCE ANALYSIS")
    print("=" * 60)

    promo = result.get("promo_details", {})
    print(f"\nPromo Type: {promo.get('promo_type', 'unknown')}")
    if promo.get('promo_title'):
        print(f"Title: {promo['promo_title']}")
    print(f"Products on Promo: {promo.get('products_on_promo', 0)}")
    print(f"Display Quality: {promo.get('display_quality', 'unknown')}")
    print(f"Signage Visible: {promo.get('signage_visible', False)}")
    print(f"Price Visible: {promo.get('price_visible', False)}")

    print(f"\nCompliance Status: {result.get('compliance_status', 'unknown').upper()}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")

    issues = result.get("issues", [])
    if issues:
        print(f"\n{'=' * 60}")
        print(f"ISSUES ({len(issues)})")
        print("=" * 60)

        for issue in issues:
            severity = issue.get('severity', 'unknown').upper()
            issue_type = issue.get('issue_type', 'unknown')
            print(f"\n[{severity}] {issue_type}")
            print(f"Description: {issue.get('description', 'N/A')}")

    print("\n" + "=" * 60 + "\n")


def print_fifo_summary(result: dict) -> None:
    """Print summary for FIFO analysis."""
    print("\n" + "=" * 60)
    print("FIFO COMPLIANCE ANALYSIS")
    print("=" * 60)

    fifo = result.get("fifo_compliance", {})
    print(f"\nFIFO Compliant: {fifo.get('compliant', 'Unknown')}")
    print(f"Products Checked: {fifo.get('total_products_checked', 0)}")
    print(f"Violations Found: {fifo.get('violations_found', 0)}")
    print(f"Overall Status: {fifo.get('overall_status', 'unknown').upper()}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")

    products = result.get("products", [])
    if products:
        print(f"\n{'=' * 60}")
        print(f"PRODUCTS CHECKED ({len(products)})")
        print("=" * 60)

        for product in products:
            print(f"\n{product.get('product_name', 'Unknown')}")
            print(f"  FIFO Status: {product.get('fifo_status', 'unknown').upper()}")
            if product.get('front_expiry_date'):
                print(f"  Front Expiry: {product['front_expiry_date']}")
            if product.get('back_expiry_date'):
                print(f"  Back Expiry: {product['back_expiry_date']}")
            if product.get('violation_details'):
                print(f"  Issue: {product['violation_details']}")
            if product.get('recommendation'):
                print(f"  Action: {product['recommendation']}")

    issues = result.get("issues", [])
    if issues:
        print(f"\n{'=' * 60}")
        print("CRITICAL ISSUES")
        print("=" * 60)

        for issue in issues:
            severity = issue.get('severity', 'unknown').upper()
            print(f"\n[{severity}] {issue.get('product_name', 'Unknown')}")
            print(f"Issue: {issue.get('issue_type', 'unknown')}")
            print(f"Details: {issue.get('description', 'N/A')}")

    print("\n" + "=" * 60 + "\n")


def print_quality_summary(result: dict) -> None:
    """Print summary for quality check."""
    print("\n" + "=" * 60)
    print("IMAGE QUALITY ASSESSMENT")
    print("=" * 60)

    suitable = result.get("suitable_for_analysis", False)
    print(f"\nSuitable for Analysis: {suitable}")
    print(f"Recommendation: {result.get('recommendation', 'unknown').upper()}")

    if result.get('blur_level'):
        print(f"\nBlur Level: {result['blur_level']}")
    if result.get('lighting'):
        print(f"Lighting: {result['lighting']}")
    if result.get('angle'):
        print(f"Angle: {result['angle']}")
    if result.get('content_visible') is not None:
        print(f"Content Visible: {result['content_visible']}")

    issues = result.get("issues", [])
    if issues:
        print(f"\nIssues Found:")
        for issue in issues:
            print(f"  - {issue}")

    print("\n" + "=" * 60 + "\n")


def print_summary(result: dict, capture_type: str) -> None:
    """Route to appropriate summary printer based on capture type."""
    if "error" in result:
        print(f"\nError during analysis: {result.get('error_message', 'Unknown error')}")
        return

    summary_printers = {
        "waste": print_waste_summary,
        "shelf": print_shelf_summary,
        "promo": print_promo_summary,
        "fifo": print_fifo_summary,
        "quality_check": print_quality_summary
    }

    printer = summary_printers.get(capture_type)
    if printer:
        printer(result)
    else:
        print(f"\nNo summary printer for capture type: {capture_type}")
        print(json.dumps(result, indent=2))


def analyze_command(args: argparse.Namespace) -> int:
    """Execute the analyze command."""
    # Validate input file
    if not Path(args.image).exists():
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        return 1

    try:
        # Initialize analyzer
        analyzer = MultiTypeComplianceAnalyzer()

        print(f"Analyzing image: {args.image}")
        print(f"Capture type: {args.type}")
        print("This may take a few moments...\n")

        # Analyze image
        if args.output:
            result = analyzer.analyze_and_save(
                args.image,
                args.type,
                args.output,
                pretty=not args.compact
            )
            print(f"Analysis complete! Results saved to: {args.output}")
        else:
            result = analyzer.analyze_image(args.image, capture_type=args.type)

        # Print summary unless quiet mode
        if not args.quiet:
            print_summary(result, args.type)

        # Print JSON if requested
        if args.json and not args.output:
            if args.compact:
                print(json.dumps(result))
            else:
                print(json.dumps(result, indent=2))

        # Exit with error code if analysis had errors
        if "error" in result:
            return 1

        return 0

    except Exception as e:
        print(f"Error during analysis: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Multi-Type Retail Compliance Analyzer - AI-powered store image analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Capture Types:
  waste          Waste/disposal/shrinkage analysis
  shelf          On-Shelf Availability (OSA) and shelf compliance
  promo          Promotional display compliance
  fifo           FIFO (First In, First Out) compliance
  quality_check  Image quality pre-assessment

Examples:
  # Analyze waste disposal
  python -m analyzer.multi_cli analyze waste_bin.jpg --type waste

  # Check shelf compliance
  python -m analyzer.multi_cli analyze shelf.jpg --type shelf

  # Verify promotional display
  python -m analyzer.multi_cli analyze endcap.jpg --type promo

  # FIFO compliance check
  python -m analyzer.multi_cli analyze cooler.jpg --type fifo

  # Quality check before full analysis
  python -m analyzer.multi_cli analyze image.jpg --type quality_check

  # Save results to JSON
  python -m analyzer.multi_cli analyze image.jpg --type waste --output report.json

  # Output JSON to stdout
  python -m analyzer.multi_cli analyze image.jpg --type shelf --json --quiet
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
        "-t", "--type",
        choices=["waste", "shelf", "promo", "fifo", "quality_check"],
        default="waste",
        help="Type of analysis to perform (default: waste)"
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
