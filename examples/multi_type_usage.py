"""
Multi-Type Analyzer Usage Examples

Demonstrates how to use the analyzer for different capture types.
"""

from analyzer import MultiTypeComplianceAnalyzer

def example_waste_analysis():
    """Analyze waste/disposal images."""
    print("=" * 60)
    print("WASTE ANALYSIS EXAMPLE")
    print("=" * 60)

    analyzer = MultiTypeComplianceAnalyzer()

    # Analyze waste image
    result = analyzer.analyze_waste("waste_image.jpg")

    print(f"Waste Reason: {result.get('waste_reason')}")
    print(f"Total Items: {result.get('estimated_total_items')}")
    print(f"Products Found: {len(result.get('products', []))}")

    for product in result.get('products', []):
        print(f"\n- {product['product_name']}")
        print(f"  Quantity: {product['quantity']} {product['unit']}")
        print(f"  Condition: {product['condition']}")
        print(f"  Issue: {product['damage_details']}")


def example_shelf_analysis():
    """Analyze shelf compliance and OSA."""
    print("\n" + "=" * 60)
    print("SHELF ANALYSIS EXAMPLE")
    print("=" * 60)

    analyzer = MultiTypeComplianceAnalyzer()

    # Analyze shelf image
    result = analyzer.analyze_shelf("shelf_image.jpg")

    overview = result.get('shelf_overview', {})
    print(f"OSA: {overview.get('osa_percentage')}%")
    print(f"Empty Facings: {overview.get('empty_facings')}")
    print(f"Compliance: {result.get('compliance_status')}")

    issues = result.get('issues', [])
    if issues:
        print(f"\nIssues Found: {len(issues)}")
        for issue in issues:
            print(f"- [{issue['severity']}] {issue['issue_type']}: {issue['description']}")


def example_promo_analysis():
    """Analyze promotional displays."""
    print("\n" + "=" * 60)
    print("PROMO ANALYSIS EXAMPLE")
    print("=" * 60)

    analyzer = MultiTypeComplianceAnalyzer()

    # Analyze promo image
    result = analyzer.analyze_promo("promo_image.jpg")

    promo = result.get('promo_details', {})
    print(f"Promo Type: {promo.get('promo_type')}")
    print(f"Display Quality: {promo.get('display_quality')}")
    print(f"Products on Promo: {promo.get('products_on_promo')}")
    print(f"Signage Visible: {promo.get('signage_visible')}")
    print(f"Compliance: {result.get('compliance_status')}")


def example_fifo_analysis():
    """Analyze FIFO compliance."""
    print("\n" + "=" * 60)
    print("FIFO ANALYSIS EXAMPLE")
    print("=" * 60)

    analyzer = MultiTypeComplianceAnalyzer()

    # Analyze FIFO compliance
    result = analyzer.analyze_fifo("cooler_image.jpg")

    fifo = result.get('fifo_compliance', {})
    print(f"FIFO Compliant: {fifo.get('compliant')}")
    print(f"Violations: {fifo.get('violations_found')}")

    for product in result.get('products', []):
        status = product.get('fifo_status')
        print(f"\n{product['product_name']}: {status}")
        if status == 'violation':
            print(f"  Issue: {product.get('violation_details')}")
            print(f"  Action: {product.get('recommendation')}")


def example_quality_check():
    """Pre-check image quality before analysis."""
    print("\n" + "=" * 60)
    print("QUALITY CHECK EXAMPLE")
    print("=" * 60)

    analyzer = MultiTypeComplianceAnalyzer()

    # Check image quality
    result = analyzer.quality_check("image.jpg")

    print(f"Suitable: {result.get('suitable_for_analysis')}")
    print(f"Recommendation: {result.get('recommendation')}")

    if not result.get('suitable_for_analysis'):
        print(f"Issues: {', '.join(result.get('issues', []))}")
        print("Please retake the image")
    else:
        print("Image quality is good - proceed with analysis")


def example_workflow():
    """Example workflow: quality check then analysis."""
    print("\n" + "=" * 60)
    print("WORKFLOW EXAMPLE")
    print("=" * 60)

    analyzer = MultiTypeComplianceAnalyzer()

    image_path = "store_image.jpg"

    # Step 1: Quality check
    quality = analyzer.quality_check(image_path)

    if not quality.get('suitable_for_analysis'):
        print("❌ Image quality insufficient")
        print(f"Recommendation: {quality.get('recommendation')}")
        return

    print("✓ Image quality check passed")

    # Step 2: Perform analysis
    result = analyzer.analyze_waste(image_path)

    print(f"✓ Analysis complete")
    print(f"  Items found: {result.get('estimated_total_items')}")
    print(f"  Confidence: {result.get('confidence'):.2f}")

    # Step 3: Save results
    analyzer.analyze_and_save(
        image_path,
        capture_type="waste",
        output_path="waste_report.json"
    )
    print("✓ Report saved")


def example_batch_multi_type():
    """Batch analysis with different capture types."""
    print("\n" + "=" * 60)
    print("BATCH MULTI-TYPE EXAMPLE")
    print("=" * 60)

    analyzer = MultiTypeComplianceAnalyzer()

    # Different images with different analysis types
    tasks = [
        ("waste_bin.jpg", "waste"),
        ("shelf_1.jpg", "shelf"),
        ("endcap.jpg", "promo"),
        ("cooler.jpg", "fifo")
    ]

    results = []

    for image_path, capture_type in tasks:
        print(f"\nAnalyzing {image_path} ({capture_type})...")

        try:
            result = analyzer.analyze_image(image_path, capture_type=capture_type)
            results.append({
                "image": image_path,
                "type": capture_type,
                "success": "error" not in result,
                "confidence": result.get("confidence", 0)
            })
            print(f"  ✓ Complete (confidence: {result.get('confidence', 0):.2f})")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            results.append({
                "image": image_path,
                "type": capture_type,
                "success": False,
                "error": str(e)
            })

    # Summary
    print(f"\n{'=' * 60}")
    print("BATCH SUMMARY")
    print("=" * 60)
    successful = sum(1 for r in results if r["success"])
    print(f"Total: {len(results)} | Success: {successful} | Failed: {len(results) - successful}")


if __name__ == "__main__":
    print("Multi-Type Compliance Analyzer Examples\n")
    print("NOTE: Replace image paths with actual files before running\n")

    # Uncomment to run specific examples:

    # example_waste_analysis()
    # example_shelf_analysis()
    # example_promo_analysis()
    # example_fifo_analysis()
    # example_quality_check()
    # example_workflow()
    # example_batch_multi_type()

    print("\nUncomment the examples you want to run in the script.")
