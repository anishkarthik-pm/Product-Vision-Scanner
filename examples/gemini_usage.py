"""
Gemini Analyzer Usage Examples

Demonstrates how to use the Gemini-based analyzer for different capture types.
"""

from analyzer import GeminiComplianceAnalyzer

def example_waste_analysis():
    """Analyze waste/disposal images with Gemini."""
    print("=" * 60)
    print("GEMINI WASTE ANALYSIS EXAMPLE")
    print("=" * 60)

    # Initialize with Gemini
    analyzer = GeminiComplianceAnalyzer()

    # Analyze waste image
    result = analyzer.analyze_waste("waste_image.jpg")

    print(f"Waste Reason: {result.get('waste_reason')}")
    print(f"Total Items: {result.get('estimated_total_items')}")
    print(f"Products Found: {len(result.get('products', []))}")
    print(f"Confidence: {result.get('confidence'):.2f}")

    for product in result.get('products', []):
        print(f"\n- {product['product_name']}")
        print(f"  Quantity: {product['quantity']} {product['unit']}")
        print(f"  Condition: {product['condition']}")
        print(f"  Issue: {product['damage_details']}")


def example_shelf_analysis():
    """Analyze shelf compliance with Gemini."""
    print("\n" + "=" * 60)
    print("GEMINI SHELF ANALYSIS EXAMPLE")
    print("=" * 60)

    analyzer = GeminiComplianceAnalyzer()

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


def example_with_quality_check():
    """Pre-check image quality before analysis."""
    print("\n" + "=" * 60)
    print("GEMINI WITH QUALITY CHECK")
    print("=" * 60)

    analyzer = GeminiComplianceAnalyzer()

    image_path = "store_image.jpg"

    # Step 1: Quality check
    print("Step 1: Checking image quality...")
    quality = analyzer.quality_check(image_path)

    print(f"Suitable: {quality.get('suitable_for_analysis')}")
    print(f"Recommendation: {quality.get('recommendation')}")

    if not quality.get('suitable_for_analysis'):
        print(f"Issues: {', '.join(quality.get('issues', []))}")
        print("Please retake the image")
        return

    # Step 2: Perform analysis
    print("\nStep 2: Running waste analysis...")
    result = analyzer.analyze_waste(image_path)

    print(f"✓ Analysis complete")
    print(f"  Items found: {result.get('estimated_total_items')}")
    print(f"  Confidence: {result.get('confidence'):.2f}")


def example_different_models():
    """Try different Gemini models."""
    print("\n" + "=" * 60)
    print("GEMINI MODEL COMPARISON")
    print("=" * 60)

    image_path = "test_image.jpg"

    # Use Flash (faster, cheaper)
    print("\n1. Using Gemini 1.5 Flash (fast)...")
    flash = GeminiComplianceAnalyzer(model="gemini-1.5-flash")
    result_flash = flash.analyze_waste(image_path)
    print(f"   Confidence: {result_flash.get('confidence', 0):.2f}")

    # Use Pro (more powerful)
    print("\n2. Using Gemini 1.5 Pro (powerful)...")
    pro = GeminiComplianceAnalyzer(model="gemini-1.5-pro")
    result_pro = pro.analyze_waste(image_path)
    print(f"   Confidence: {result_pro.get('confidence', 0):.2f}")


def example_save_to_json():
    """Analyze and save results."""
    print("\n" + "=" * 60)
    print("GEMINI SAVE TO JSON")
    print("=" * 60)

    analyzer = GeminiComplianceAnalyzer()

    # Analyze and save
    result = analyzer.analyze_and_save(
        image_path="waste_image.jpg",
        capture_type="waste",
        output_path="gemini_waste_report.json",
        pretty=True
    )

    print(f"✓ Report saved to gemini_waste_report.json")
    print(f"  Total items: {result.get('estimated_total_items')}")
    print(f"  Confidence: {result.get('confidence'):.2f}")


def example_all_capture_types():
    """Demonstrate all capture types with Gemini."""
    print("\n" + "=" * 60)
    print("GEMINI ALL CAPTURE TYPES")
    print("=" * 60)

    analyzer = GeminiComplianceAnalyzer()

    tasks = [
        ("waste_image.jpg", "waste", analyzer.analyze_waste),
        ("shelf_image.jpg", "shelf", analyzer.analyze_shelf),
        ("promo_image.jpg", "promo", analyzer.analyze_promo),
        ("cooler_image.jpg", "fifo", analyzer.analyze_fifo),
    ]

    for image_path, capture_type, method in tasks:
        print(f"\n{capture_type.upper()} Analysis:")
        try:
            result = method(image_path)
            if "error" in result:
                print(f"  ✗ Error: {result['error_message']}")
            else:
                print(f"  ✓ Success (confidence: {result.get('confidence', 0):.2f})")
        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")


def simple_example():
    """Simplest possible example."""
    print("\n" + "=" * 60)
    print("SIMPLE GEMINI EXAMPLE")
    print("=" * 60)

    from analyzer import GeminiComplianceAnalyzer

    # Just 3 lines!
    analyzer = GeminiComplianceAnalyzer()
    result = analyzer.analyze_waste("waste_image.jpg")
    print(f"Found {result.get('estimated_total_items')} items with {result.get('confidence'):.0%} confidence")


if __name__ == "__main__":
    print("Gemini Compliance Analyzer Examples\n")
    print("NOTE: Replace image paths with actual files before running\n")

    # Uncomment to run specific examples:

    # example_waste_analysis()
    # example_shelf_analysis()
    # example_with_quality_check()
    # example_different_models()
    # example_save_to_json()
    # example_all_capture_types()
    # simple_example()

    print("\nUncomment the examples you want to run in the script.")
