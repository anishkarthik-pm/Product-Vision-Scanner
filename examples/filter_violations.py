"""
Violation filtering example

Analyze an image and filter for specific types of compliance violations.
"""

from analyzer import RetailComplianceAnalyzer

def filter_violations(result: dict, severity: str = None, violation_type: str = None):
    """
    Filter products by violation criteria.

    Args:
        result: Analysis result dictionary
        severity: Filter by severity (critical, high, medium, low)
        violation_type: Filter by type (expired, damaged, etc.)

    Returns:
        List of products matching the criteria
    """
    filtered_products = []

    for product in result.get("products", []):
        violations = product.get("compliance", {}).get("violations", [])

        for violation in violations:
            # Check filters
            if severity and violation.get("severity") != severity:
                continue

            if violation_type and violation.get("type") != violation_type:
                continue

            # Add product with violation details
            filtered_products.append({
                "product": product.get("name", "Unknown"),
                "brand": product.get("brand"),
                "violation": violation,
                "confidence": product.get("confidence")
            })

    return filtered_products

def main():
    analyzer = RetailComplianceAnalyzer()

    # Analyze image
    image_path = "store_image.jpg"
    result = analyzer.analyze_image(image_path)

    # Find all critical violations
    print("CRITICAL VIOLATIONS:")
    critical = filter_violations(result, severity="critical")
    for item in critical:
        print(f"- {item['product']} ({item['brand']})")
        print(f"  Issue: {item['violation']['description']}")
        print(f"  Type: {item['violation']['type']}")
        print()

    # Find all expired products
    print("\nEXPIRED PRODUCTS:")
    expired = filter_violations(result, violation_type="expired")
    for item in expired:
        print(f"- {item['product']} ({item['brand']})")
        print(f"  Severity: {item['violation']['severity']}")
        print()

    # Find damaged products
    print("\nDAMAGED PRODUCTS:")
    damaged = filter_violations(result, violation_type="damaged")
    for item in damaged:
        print(f"- {item['product']} ({item['brand']})")
        print(f"  Issue: {item['violation']['description']}")
        print()

if __name__ == "__main__":
    main()
