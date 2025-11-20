"""
Basic usage example for Retail Compliance Analyzer

This script demonstrates the simplest way to analyze a store image.
"""

from analyzer import RetailComplianceAnalyzer

def main():
    # Initialize the analyzer
    analyzer = RetailComplianceAnalyzer()

    # Analyze an image
    image_path = "store_image.jpg"  # Replace with your image path

    print(f"Analyzing {image_path}...")
    result = analyzer.analyze_image(image_path)

    # Print basic information
    print(f"\nAnalysis Status: {result['analysis_status']}")
    print(f"Total Products Found: {result['overall_compliance']['total_products']}")
    print(f"Compliant Products: {result['overall_compliance']['compliant_count']}")
    print(f"Violations Found: {result['overall_compliance']['violation_count']}")

    # Show each product
    for product in result['products']:
        print(f"\n- {product.get('name', 'Unknown')} ({product.get('brand', 'N/A')})")
        print(f"  Condition: {product['condition']['status']}")
        print(f"  Compliant: {product['compliance'].get('is_compliant', 'unclear')}")
        print(f"  Confidence: {product['confidence']:.2f}")

if __name__ == "__main__":
    main()
