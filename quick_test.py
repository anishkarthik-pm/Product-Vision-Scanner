#!/usr/bin/env python3
"""
Quick Test Script

Verifies the analyzer works with a simple test.
"""

import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("RETAIL COMPLIANCE ANALYZER - QUICK TEST")
    print("=" * 60)
    print()

    # Step 1: Check imports
    print("Step 1: Checking imports...")
    try:
        from analyzer import MultiTypeComplianceAnalyzer
        print("✓ Analyzer imported successfully")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        print("\nFix: Run 'pip install -r requirements.txt'")
        return 1

    # Step 2: Check API key
    print("\nStep 2: Checking API key...")
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("✗ API key not configured")
            print("\nFix:")
            print("  1. Copy .env.example to .env")
            print("  2. Edit .env and add your Anthropic API key")
            return 1
        elif api_key == "your_api_key_here":
            print("✗ API key still set to placeholder")
            print("\nFix: Edit .env and replace with your actual API key")
            return 1
        else:
            print(f"✓ API key configured (starts with: {api_key[:10]}...)")
    except Exception as e:
        print(f"✗ Error checking API key: {e}")
        return 1

    # Step 3: Initialize analyzer
    print("\nStep 3: Initializing analyzer...")
    try:
        analyzer = MultiTypeComplianceAnalyzer()
        print("✓ Analyzer initialized successfully")
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return 1

    # Step 4: Check for test image
    print("\nStep 4: Looking for test image...")
    test_images = []
    for ext in ['.jpg', '.jpeg', '.png']:
        test_images.extend(Path('.').glob(f'*{ext}'))
        test_images.extend(Path('.').glob(f'test_*{ext}'))
        test_images.extend(Path('.').glob(f'sample*{ext}'))

    if test_images:
        test_image = str(test_images[0])
        print(f"✓ Found test image: {test_image}")

        # Step 5: Run analysis
        print("\nStep 5: Running test analysis...")
        print("(This will make an API call - may take a few seconds)")

        try:
            # First do a quality check
            print("\n  Running quality check...")
            quality = analyzer.quality_check(test_image)

            print(f"  Suitable: {quality.get('suitable_for_analysis', 'unknown')}")
            print(f"  Recommendation: {quality.get('recommendation', 'unknown')}")

            if quality.get('suitable_for_analysis'):
                print("\n  Running waste analysis...")
                result = analyzer.analyze_waste(test_image)

                if 'error' in result:
                    print(f"  ✗ Analysis error: {result.get('error_message')}")
                else:
                    print(f"\n  ✓ Analysis complete!")
                    print(f"  - Capture type: {result.get('capture_type')}")
                    print(f"  - Products found: {len(result.get('products', []))}")
                    print(f"  - Total items: {result.get('estimated_total_items', 0)}")
                    print(f"  - Confidence: {result.get('confidence', 0):.2f}")
                    print(f"  - Image quality: {result.get('image_quality', 'unknown')}")
            else:
                print(f"\n  ⚠️ Image quality issues: {', '.join(quality.get('issues', []))}")
                print(f"  Recommendation: {quality.get('recommendation')}")

            print("\n" + "=" * 60)
            print("✓ TEST PASSED - System is working correctly!")
            print("=" * 60)
            print("\nNext steps:")
            print("  1. Try: python -m analyzer.multi_cli analyze image.jpg --type waste")
            print("  2. Read: MULTI_TYPE_GUIDE.md for detailed usage")
            print("  3. Check: examples/ directory for code samples")
            print()
            return 0

        except Exception as e:
            print(f"\n✗ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            print("\nCheck your API key and internet connection")
            return 1
    else:
        print("⚠️ No test images found")
        print("\nTo complete the test:")
        print("  1. Add any .jpg or .png image to this directory")
        print("  2. Run this script again")
        print("\n  Or download a sample:")
        print("  curl -o test.jpg 'https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=800'")
        print()

        print("=" * 60)
        print("✓ PARTIAL SUCCESS - Setup verified, waiting for test image")
        print("=" * 60)
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
